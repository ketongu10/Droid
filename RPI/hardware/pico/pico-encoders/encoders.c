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

static void init_LED() {
    stdio_init_all();
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
}


static const uint DELTA = 2;
static const uint MIN_TICKS_SINCE_STARTED = 0;
static long position_in_degrees = 0;
static const uint MOTOR_1A_FORWARD = 2;
static const uint MOTOR_1A_BACKWARD = 3;

static void read_MINDSTORM_encoders(uint forward, uint backward) {
    bool started = false;
    uint ticks = 0;
    bool f,b;
    uint ind = 0;
    context.mem[127] = 11;
    while (1) {
        ind++;
        f = gpio_get(forward);
        b = gpio_get(backward);
        if (!started) {
            if (f && b) {
                started = true;
            }
        } else {
            ticks+=1;
            if (f && !b && ticks >= MIN_TICKS_SINCE_STARTED) {
                position_in_degrees+=DELTA;
                started = false;
                ticks = 0;
            }
            if (!f && b && ticks >= MIN_TICKS_SINCE_STARTED) {
                position_in_degrees-=DELTA;
                started = false;
                ticks = 0;
            }
        }
        context.mem[254] = (uint8_t)(ind & 0xFF);
        context.mem[255] = (uint8_t)(position_in_degrees & 0xFF);
        sleep_ms(10);
    }
}

struct Mencoder{
    uint forward;
    uint backward;
    bool started;
    uint ticks;
    long position_in_degrees;

};


// static void read_MINDSTORM_encoder(Mencoder* encoder) {
//     f = gpio_get(encoder->forward);
//     b = gpio_get(encoder->backward);
//     if (!encoder->started) {
//         if (f && b) {
//             encoder->started = true;
//         }
//     } else {
//         encoder->ticks+=1;
//         if (f && !b && encoder->ticks >= MIN_TICKS_SINCE_STARTED) {
//             encoder->position_in_degrees+=DELTA;
//             encoder->started = false;
//             encoder->ticks = 0;
//         }
//         if (!f && b && encoder->ticks >= MIN_TICKS_SINCE_STARTED) {
//             encoder->position_in_degrees-=DELTA;
//             encoder->started = false;
//             encoder->ticks = 0;
//         }
//     }

// }


static const uint MENCODER_FORWARD = 2;
static const uint MENCODER_BACKWARD = 3;




static void init_gpios() {
    gpio_init(MENCODER_FORWARD);
    gpio_init(MENCODER_BACKWARD);
    gpio_set_dir(MENCODER_FORWARD, GPIO_IN);
    gpio_set_dir(MENCODER_BACKWARD, GPIO_IN);
}







static struct Mencoder enc1 = {0, 0, false, 0, 0};

int main() {
    stdio_init_all();
    init_gpios();
    setup_slave();
    read_MINDSTORM_encoders(MENCODER_FORWARD, MENCODER_BACKWARD);
    // while (1) {
    //     read_MINDSTORM_encoder(&enc1);
    // }

}
