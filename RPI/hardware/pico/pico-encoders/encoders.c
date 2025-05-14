#include "hardware/gpio.h"
#include "pico/binary_info.h"
#include <hardware/i2c.h>
#include "hardware/adc.h"
#include "hardware/irq.h"
#include "hardware/pwm.h"
#include <pico/i2c_slave.h>
#include <pico/stdlib.h>
#include <stdio.h>
#include <string.h>
#include "hardware/timer.h"



static const uint I2C_SLAVE_ADDRESS = 0x27;
static const uint I2C_BAUDRATE = 400000; // 100 kHz
static const uint DC_INPUT = 28;
static const float conversion_factor = 3.3f / (1 << 12);


// For this example, we run both the master and slave from the same board.
// You'll need to wire pin GP4 to GP6 (SDA), and pin GP5 to GP7 (SCL).
static const uint I2C_SLAVE_SDA_PIN = PICO_DEFAULT_I2C_SDA_PIN; // 4
static const uint I2C_SLAVE_SCL_PIN = PICO_DEFAULT_I2C_SCL_PIN; // 5
const uint LED_PIN = 25;

// The slave implements a 256 byte memory. To write a series of bytes, the master first
// writes the memory address, followed by the data. The address is automatically incremented
// for each byte transferred, looping back to 0 upon reaching the end. Reading is done
// sequentially from the current memory address.
static struct
{
    uint8_t mem[256];
    uint8_t mem_address;
    bool mem_address_written;
} context;

// Our handler is called from the I2C ISR, so it must complete quickly. Blocking calls /
// printing to stdio may interfere with interrupt handling.
static void i2c_slave_handler(i2c_inst_t *i2c, i2c_slave_event_t event) {
    switch (event) {
    case I2C_SLAVE_RECEIVE: // master has written some data
        if (!context.mem_address_written) {
            // writes always start with the memory address
            context.mem_address = i2c_read_byte_raw(i2c);
            context.mem_address_written = true;
        } else {
            // save into memory
            context.mem[context.mem_address] = i2c_read_byte_raw(i2c);
            context.mem_address++;
        }
        break;
    case I2C_SLAVE_REQUEST: // master is requesting data
        // load from memory
        i2c_write_byte_raw(i2c, context.mem[context.mem_address]);
        context.mem_address++;
        break;
    case I2C_SLAVE_FINISH: // master has signalled Stop / Restart
        context.mem_address_written = false;
        break;
    default:
        break;
    }
}

static void setup_slave() {
    gpio_init(I2C_SLAVE_SDA_PIN);
    gpio_set_function(I2C_SLAVE_SDA_PIN, GPIO_FUNC_I2C);
    gpio_pull_up(I2C_SLAVE_SDA_PIN);

    gpio_init(I2C_SLAVE_SCL_PIN);
    gpio_set_function(I2C_SLAVE_SCL_PIN, GPIO_FUNC_I2C);
    gpio_pull_up(I2C_SLAVE_SCL_PIN);

    i2c_init(i2c0, I2C_BAUDRATE);
    // configure I2C0 for slave mode
    i2c_slave_init(i2c0, I2C_SLAVE_ADDRESS, &i2c_slave_handler);

}

// Note on RP2350 timer_hw is the default timer instance (as per PICO_DEFAULT_TIMER)

/// \tag::get_time[]
// Simplest form of getting 64 bit time from the timer.
// It isn't safe when called from 2 cores because of the latching
// so isn't implemented this way in the sdk
static uint64_t get_time(void) {
    // Reading low latches the high value
    uint32_t lo = timer_hw->timelr;
    uint32_t hi = timer_hw->timehr;
    return ((uint64_t) hi << 32u) | lo;
}


static uint64_t calc_iter_time(uint64_t start_time, uint64_t aver_dt, uint64_t num) {
    uint64_t dt = get_time() - start_time;
    uint64_t new_aver = (aver_dt*num+dt)/(num+1);
    unsigned char *p = (void *)&dt;
    for (int i=7; i>=0; i--) {
        context.mem[7-i] = (uint8_t)p[i];
    }
    return new_aver;

}

static void heavy_load(uint64_t n) {
    uint64_t sum = 0;
    for(uint64_t i=0;i<n;i++) {
        sum+=i;
    }
}

static void init_LED() {
    stdio_init_all();
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
}

static void init_DC() {
    stdio_init_all();
    adc_init();
    adc_gpio_init(28);
    adc_gpio_init(27);
    adc_gpio_init(26);
    adc_select_input(2);
}

static const uint DELTA = 2;
static const uint MIN_TICKS_SINCE_STARTED = 0;
static long position_in_degrees = 0;
static const uint MOTOR_1A_FORWARD = 2;
static const uint MOTOR_1A_BACKWARD = 3;



typedef struct {
    uint forward;
    uint backward;
    bool started;
    uint ticks;
    long position_in_degrees;
    uint DELTA; //2
    uint MIN_TICKS_SINCE_STARTED; //0
    uint buf_ind;
} Mencoder;

static void read_MINDSTORM_encoder(Mencoder* encoder) {
    bool f = gpio_get(encoder->forward);
    bool b = gpio_get(encoder->backward);

    context.mem[encoder->buf_ind-2] = (uint8_t)(b)+0xb0; //debug. signal B state
    context.mem[encoder->buf_ind-3] = (uint8_t)(f)+0xa0; //debug. signal A state
    if (!encoder->started) {
        if (f && b) {
            encoder->started = true;
        }
    } else {
        encoder->ticks+=1;
        if (f && !b && encoder->ticks >= encoder->MIN_TICKS_SINCE_STARTED) {
            encoder->position_in_degrees+=encoder->DELTA;
            encoder->started = false;
            encoder->ticks = 0;
        }
        if (!f && b && encoder->ticks >= encoder->MIN_TICKS_SINCE_STARTED) {
            encoder->position_in_degrees-=encoder->DELTA;
            encoder->started = false;
            encoder->ticks = 0;
        }

        context.mem[encoder->buf_ind-1] = (uint8_t)(encoder->position_in_degrees >> 8);
        context.mem[encoder->buf_ind] = (uint8_t)(encoder->position_in_degrees & 0xFF);
    }
    encoder->ticks+=1;

}


 typedef struct {
    uint forward;
    uint backward;
    int started;
    uint ticks;
    long position_in_degrees;
    uint DELTA; //2
    uint MIN_TICKS_SINCE_STARTED; //0
    uint buf_ind;
} EC100encoder;

typedef struct {
    uint ticks;
    long sum;
    uint max;
    uint pico_ind;
    uint buf_ind;

} AnalogInput;

static void read_EC100_encoder(EC100encoder* encoder) {
    bool f = gpio_get(encoder->forward);
    bool b = gpio_get(encoder->backward);

    context.mem[encoder->buf_ind-2] = (uint8_t)(b)+0xb0; //debug. signal B state
    context.mem[encoder->buf_ind-3] = (uint8_t)(f)+0xa0; //debug. signal A state
    if (encoder->started == 0) {
        if (f && b && encoder->ticks >= encoder->MIN_TICKS_SINCE_STARTED) {
            encoder->started = 1;
            encoder->ticks = 0;
        }
        if (!f && !b && encoder->ticks >= encoder->MIN_TICKS_SINCE_STARTED) {
            encoder->started = -1;
            encoder->ticks = 0;
        }
    } else {
        if (f && !b && encoder->ticks >= encoder->MIN_TICKS_SINCE_STARTED) {
            encoder->position_in_degrees+=encoder->DELTA*encoder->started;
            encoder->started = 0;
            encoder->ticks = 0;
        }
        if (!f && b && encoder->ticks >= encoder->MIN_TICKS_SINCE_STARTED) {
            encoder->position_in_degrees-=encoder->DELTA*encoder->started;
            encoder->started = 0;
            encoder->ticks = 0;
        }

        context.mem[encoder->buf_ind-1] = (uint8_t)(encoder->position_in_degrees >> 8);
        context.mem[encoder->buf_ind] = (uint8_t)(encoder->position_in_degrees & 0xFF);
    }
    encoder->ticks+=1;

 }

// MINDSTORMS
static const uint MENCODER_FORWARD_1 = 0;
static const uint MENCODER_BACKWARD_1 = 1;
static const uint MENCODER_FORWARD_2 = 2;
static const uint MENCODER_BACKWARD_2 = 3;
static const uint MENCODER_FORWARD_3 = 6;
static const uint MENCODER_BACKWARD_3 = 7;
static const uint MENCODER_FORWARD_4 = 8;
static const uint MENCODER_BACKWARD_4 = 9;
static const uint MENCODER_FORWARD_5 = 10;
static const uint MENCODER_BACKWARD_5 = 11;
static const uint MENCODER_FORWARD_6 = 12;
static const uint MENCODER_BACKWARD_6 = 13;




static void init_gpios() {
    gpio_init(MENCODER_FORWARD_1);
    gpio_init(MENCODER_BACKWARD_1);
    gpio_set_dir(MENCODER_FORWARD_1, GPIO_IN);
    gpio_set_dir(MENCODER_BACKWARD_1, GPIO_IN);
    gpio_init(MENCODER_FORWARD_2);
    gpio_init(MENCODER_BACKWARD_2);
    gpio_set_dir(MENCODER_FORWARD_2, GPIO_IN);
    gpio_set_dir(MENCODER_BACKWARD_2, GPIO_IN);
    gpio_init(MENCODER_FORWARD_3);
    gpio_init(MENCODER_BACKWARD_3);
    gpio_set_dir(MENCODER_FORWARD_3, GPIO_IN);
    gpio_set_dir(MENCODER_BACKWARD_3, GPIO_IN);
    gpio_init(MENCODER_FORWARD_4);
    gpio_init(MENCODER_BACKWARD_4);
    gpio_set_dir(MENCODER_FORWARD_4, GPIO_IN);
    gpio_set_dir(MENCODER_BACKWARD_4, GPIO_IN);
    gpio_init(MENCODER_FORWARD_5);
    gpio_init(MENCODER_BACKWARD_5);
    gpio_set_dir(MENCODER_FORWARD_5, GPIO_IN);
    gpio_set_dir(MENCODER_BACKWARD_5, GPIO_IN);
    gpio_init(MENCODER_FORWARD_6);
    gpio_init(MENCODER_BACKWARD_6);
    gpio_set_dir(MENCODER_FORWARD_6, GPIO_IN);
    gpio_set_dir(MENCODER_BACKWARD_6, GPIO_IN);
}



static void read_analog(AnalogInput* pin) {


    if (pin->ticks == pin->max) {
        pin->sum =(long) (pin->sum / pin->max);
        context.mem[pin->buf_ind-1] = (uint8_t)(pin->sum >> 8);
        context.mem[pin->buf_ind] = (uint8_t)(pin->sum & 0xFF);
        pin->ticks = 0;
    } else {
        adc_select_input(pin->pico_ind);
        pin->sum += adc_read();
        pin->ticks+=1;
    }


}


Mencoder enc1 = {MENCODER_FORWARD_1, MENCODER_BACKWARD_1, false, 0, 0, 2, 0, 255-16*5};
EC100encoder enc2 = {MENCODER_FORWARD_2, MENCODER_BACKWARD_2, 0, 0, 0, 1, 100, 255-16*4};
Mencoder enc3 = {MENCODER_FORWARD_3, MENCODER_BACKWARD_3, false, 0, 0, 2, 0, 255-16*3};
Mencoder enc4 = {MENCODER_FORWARD_4, MENCODER_BACKWARD_4, false, 0, 0, 2, 0, 255-16*2};
Mencoder enc5 = {MENCODER_FORWARD_5, MENCODER_BACKWARD_5, false, 0, 0, 2, 0, 255-16};
Mencoder enc6 = {MENCODER_FORWARD_6, MENCODER_BACKWARD_6, false, 0, 0, 2, 0, 255};

AnalogInput pin0 = {0, 0, 100, 0, 15};
AnalogInput pin1 = {0, 0, 100, 1, 15+16};
AnalogInput pin2 = {0, 0, 100, 2, 15+16*2};

int main() {
    stdio_init_all();
    init_gpios();
    setup_slave();
    init_DC();

    uint64_t start_time;
    uint64_t aver_time=0;
    uint64_t num;

    context.mem[127] = 11;
//    read_MINDSTORM_encoders(MENCODER_FORWARD, MENCODER_BACKWARD);
    while (1) {
        start_time = get_time();
        read_MINDSTORM_encoder(&enc1);
        read_EC100_encoder(&enc2);
        read_MINDSTORM_encoder(&enc3);
        read_MINDSTORM_encoder(&enc4);
        read_MINDSTORM_encoder(&enc5);
        read_MINDSTORM_encoder(&enc6);
        read_analog(&pin0);
        read_analog(&pin1);
        read_analog(&pin2);
        aver_time = calc_iter_time(start_time, aver_time, num);
        num++;
        sleep_ms(0.5);

    }

}
