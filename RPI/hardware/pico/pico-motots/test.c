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

static const uint I2C_SLAVE_ADDRESS = 0x17;
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


static void init_DC() {
    stdio_init_all();
    adc_init();
    adc_gpio_init(DC_INPUT);
    adc_select_input(2);
}

static void init_PWM() {
    gpio_set_function(PICO_DEFAULT_LED_PIN, GPIO_FUNC_PWM);
    uint slice_num = pwm_gpio_to_slice_num(PICO_DEFAULT_LED_PIN);
    pwm_config config = pwm_get_default_config();
    pwm_config_set_clkdiv(&config, 4.f);
    pwm_init(slice_num, &config, true);
}


static int fade = 0;
static bool going_up = true;
void pwm_led() {
    if (context.mem[0] == 0x01) {
        
     

        if (going_up) {
            ++fade;
            if (fade > 255) {
                fade = 255;
                going_up = false;
            }
        } else {
            --fade;
            if (fade < 0) {
                fade = 0;
                going_up = true;
            }
        }
        // Square the fade value to make the LED's brightness appear more linear
        // Note this range matches with the wrap value
        pwm_set_gpio_level(PICO_DEFAULT_LED_PIN, fade * fade);
    } else {
        pwm_set_gpio_level(PICO_DEFAULT_LED_PIN, 0);
    }
}



static const uint DRIVER_1_OK = 27;
static const uint MOTOR_1A_FORWARD = 26;
static const uint MOTOR_1A_BACKWARD = 2;
static const uint MOTOR_1A_PWM = 3;
static const uint MOTOR_1B_FORWARD = 6;
static const uint MOTOR_1B_BACKWARD = 7;
static const uint MOTOR_1B_PWM = 8;

static const uint DRIVER_2_OK = 9;
static const uint MOTOR_2A_FORWARD = 10;
static const uint MOTOR_2A_BACKWARD = 11;
static const uint MOTOR_2A_PWM = 12;
static const uint MOTOR_2B_FORWARD = 13;
static const uint MOTOR_2B_BACKWARD = 14;
static const uint MOTOR_2B_PWM = 15;


static const uint DRIVER_3_OK = 22;
static const uint MOTOR_3A_FORWARD = 21;
static const uint MOTOR_3A_BACKWARD = 20;
static const uint MOTOR_3A_PWM = 19;
static const uint MOTOR_3B_FORWARD = 18;
static const uint MOTOR_3B_BACKWARD = 17;
static const uint MOTOR_3B_PWM = 16;



static const uint DEFAULT_PWM_LEVEL = 32512;

static void init_MOTORS() {
    gpio_set_function(MOTOR_1A_PWM, GPIO_FUNC_PWM);
    gpio_set_function(MOTOR_1B_PWM, GPIO_FUNC_PWM);
    gpio_set_function(MOTOR_2A_PWM, GPIO_FUNC_PWM);
    gpio_set_function(MOTOR_2B_PWM, GPIO_FUNC_PWM);
    gpio_set_function(MOTOR_3A_PWM, GPIO_FUNC_PWM);
    gpio_set_function(MOTOR_3B_PWM, GPIO_FUNC_PWM);
    gpio_init(MOTOR_1A_FORWARD);
    gpio_init(MOTOR_1A_BACKWARD);
    gpio_init(MOTOR_1B_FORWARD);
    gpio_init(MOTOR_1B_BACKWARD);
    gpio_init(MOTOR_2A_FORWARD);
    gpio_init(MOTOR_2A_BACKWARD);
    gpio_init(MOTOR_2B_FORWARD);
    gpio_init(MOTOR_2B_BACKWARD);
    gpio_init(MOTOR_3A_FORWARD);
    gpio_init(MOTOR_3A_BACKWARD);
    gpio_init(MOTOR_3B_FORWARD);
    gpio_init(MOTOR_3B_BACKWARD);
    gpio_init(DRIVER_1_OK);
    gpio_init(DRIVER_2_OK);
    gpio_init(DRIVER_3_OK);
    gpio_set_dir(MOTOR_1A_FORWARD, GPIO_OUT);
    gpio_set_dir(MOTOR_1A_BACKWARD, GPIO_OUT);
    gpio_set_dir(MOTOR_1B_FORWARD, GPIO_OUT);
    gpio_set_dir(MOTOR_1B_BACKWARD, GPIO_OUT);
    gpio_set_dir(MOTOR_2A_FORWARD, GPIO_OUT);
    gpio_set_dir(MOTOR_2A_BACKWARD, GPIO_OUT);
    gpio_set_dir(MOTOR_2B_FORWARD, GPIO_OUT);
    gpio_set_dir(MOTOR_2B_BACKWARD, GPIO_OUT);
    gpio_set_dir(MOTOR_3A_FORWARD, GPIO_OUT);
    gpio_set_dir(MOTOR_3A_BACKWARD, GPIO_OUT);
    gpio_set_dir(MOTOR_3B_FORWARD, GPIO_OUT);
    gpio_set_dir(MOTOR_3B_BACKWARD, GPIO_OUT);
    gpio_set_dir(DRIVER_1_OK, GPIO_OUT);
    gpio_set_dir(DRIVER_2_OK, GPIO_OUT);
    gpio_set_dir(DRIVER_3_OK, GPIO_OUT);
    gpio_put(MOTOR_1A_FORWARD, 0);
    gpio_put(MOTOR_1A_BACKWARD, 0);
    gpio_put(MOTOR_1B_FORWARD, 0);
    gpio_put(MOTOR_1B_BACKWARD, 0);
    gpio_put(MOTOR_2A_FORWARD, 0);
    gpio_put(MOTOR_2A_BACKWARD, 0);
    gpio_put(MOTOR_2B_FORWARD, 0);
    gpio_put(MOTOR_2B_BACKWARD, 0);
    gpio_put(MOTOR_3A_FORWARD, 0);
    gpio_put(MOTOR_3A_BACKWARD, 0);
    gpio_put(MOTOR_3B_FORWARD, 0);
    gpio_put(MOTOR_3B_BACKWARD, 0);
    gpio_put(DRIVER_1_OK, 1);
    gpio_put(DRIVER_2_OK, 1);
    gpio_put(DRIVER_3_OK, 1);
    uint slice_num_1A = pwm_gpio_to_slice_num(MOTOR_1A_PWM);
    uint slice_num_1B = pwm_gpio_to_slice_num(MOTOR_1B_PWM);
    uint slice_num_2A = pwm_gpio_to_slice_num(MOTOR_2A_PWM);
    uint slice_num_2B = pwm_gpio_to_slice_num(MOTOR_2B_PWM);
    uint slice_num_3A = pwm_gpio_to_slice_num(MOTOR_3A_PWM);
    uint slice_num_3B = pwm_gpio_to_slice_num(MOTOR_3B_PWM);
    pwm_config config = pwm_get_default_config();
    pwm_config_set_clkdiv(&config, 4.f);
    pwm_init(slice_num_1A, &config, true);
    pwm_init(slice_num_1B, &config, true);
    pwm_init(slice_num_2A, &config, true);
    pwm_init(slice_num_2B, &config, true);
    pwm_init(slice_num_3A, &config, true);
    pwm_init(slice_num_3B, &config, true);
    pwm_set_gpio_level(MOTOR_1A_PWM, DEFAULT_PWM_LEVEL);
    pwm_set_gpio_level(MOTOR_1B_PWM, DEFAULT_PWM_LEVEL);
    pwm_set_gpio_level(MOTOR_2A_PWM, DEFAULT_PWM_LEVEL);
    pwm_set_gpio_level(MOTOR_2B_PWM, DEFAULT_PWM_LEVEL);
    pwm_set_gpio_level(MOTOR_3A_PWM, DEFAULT_PWM_LEVEL);
    pwm_set_gpio_level(MOTOR_3B_PWM, DEFAULT_PWM_LEVEL);
}

static void use_motors() {

    // DRIVER 3
    if (context.mem[0] == 0x01) {
        gpio_put(MOTOR_3A_FORWARD, 1); 
        gpio_put(MOTOR_3A_BACKWARD, 0);
        pwm_set_gpio_level(MOTOR_3A_PWM, ((uint)context.mem[1])*0xFF);
    } else if (context.mem[0] == 0x02) {
        gpio_put(MOTOR_3A_FORWARD, 0); 
        gpio_put(MOTOR_3A_BACKWARD, 1);
        pwm_set_gpio_level(MOTOR_3A_PWM, ((uint)context.mem[1])*0xFF);
    } else {
        gpio_put(MOTOR_3A_FORWARD, 0); 
        gpio_put(MOTOR_3A_BACKWARD, 0);
        pwm_set_gpio_level(MOTOR_3A_PWM, DEFAULT_PWM_LEVEL);
    }

    if (context.mem[2] == 0x01) {
        gpio_put(MOTOR_3B_FORWARD, 1); 
        gpio_put(MOTOR_3B_BACKWARD, 0);
        pwm_set_gpio_level(MOTOR_3B_PWM, ((uint)context.mem[3])*0xFF);
    } else if (context.mem[2] == 0x02) {
        gpio_put(MOTOR_3B_FORWARD, 0); 
        gpio_put(MOTOR_3B_BACKWARD, 1);
        pwm_set_gpio_level(MOTOR_3B_PWM, ((uint)context.mem[3])*0xFF);
    } else {
        gpio_put(MOTOR_3B_FORWARD, 0); 
        gpio_put(MOTOR_3B_BACKWARD, 0);
        pwm_set_gpio_level(MOTOR_3B_PWM, DEFAULT_PWM_LEVEL);
    }

    // DRIVER 2
    if (context.mem[4] == 0x01) {
        gpio_put(MOTOR_2A_FORWARD, 1); 
        gpio_put(MOTOR_2A_BACKWARD, 0);
        pwm_set_gpio_level(MOTOR_2A_PWM, ((uint)context.mem[5])*0xFF);
    } else if (context.mem[4] == 0x02) {
        gpio_put(MOTOR_2A_FORWARD, 0); 
        gpio_put(MOTOR_2A_BACKWARD, 1);
        pwm_set_gpio_level(MOTOR_2A_PWM, ((uint)context.mem[5])*0xFF);
    } else {
        gpio_put(MOTOR_2A_FORWARD, 0); 
        gpio_put(MOTOR_2A_BACKWARD, 0);
        pwm_set_gpio_level(MOTOR_2A_PWM, DEFAULT_PWM_LEVEL);
    }

    if (context.mem[6] == 0x01) {
        gpio_put(MOTOR_2B_FORWARD, 1); 
        gpio_put(MOTOR_2B_BACKWARD, 0);
        pwm_set_gpio_level(MOTOR_2B_PWM, ((uint)context.mem[7])*0xFF);
    } else if (context.mem[6] == 0x02) {
        gpio_put(MOTOR_2B_FORWARD, 0); 
        gpio_put(MOTOR_2B_BACKWARD, 1);
        pwm_set_gpio_level(MOTOR_2B_PWM, ((uint)context.mem[7])*0xFF);
    } else {
        gpio_put(MOTOR_2B_FORWARD, 0); 
        gpio_put(MOTOR_2B_BACKWARD, 0);
        pwm_set_gpio_level(MOTOR_2B_PWM, DEFAULT_PWM_LEVEL);
    }

    // DRIVER 1
    if (context.mem[8] == 0x01) {
        gpio_put(MOTOR_1A_FORWARD, 1); 
        gpio_put(MOTOR_1A_BACKWARD, 0);
        pwm_set_gpio_level(MOTOR_1A_PWM, ((uint)context.mem[9])*0xFF);
    } else if (context.mem[8] == 0x02) {
        gpio_put(MOTOR_1A_FORWARD, 0); 
        gpio_put(MOTOR_1A_BACKWARD, 1);
        pwm_set_gpio_level(MOTOR_1A_PWM, ((uint)context.mem[9])*0xFF);
    } else {
        gpio_put(MOTOR_1A_FORWARD, 0); 
        gpio_put(MOTOR_1A_BACKWARD, 0);
        pwm_set_gpio_level(MOTOR_1A_PWM, DEFAULT_PWM_LEVEL);
    }

    if (context.mem[10] == 0x01) {
        gpio_put(MOTOR_1B_FORWARD, 1); 
        gpio_put(MOTOR_1B_BACKWARD, 0);
        pwm_set_gpio_level(MOTOR_1B_PWM, ((uint)context.mem[11])*0xFF);
    } else if (context.mem[10] == 0x02) {
        gpio_put(MOTOR_1B_FORWARD, 0); 
        gpio_put(MOTOR_1B_BACKWARD, 1);
        pwm_set_gpio_level(MOTOR_1B_PWM, ((uint)context.mem[11])*0xFF);
    } else {
        gpio_put(MOTOR_1B_FORWARD, 0); 
        gpio_put(MOTOR_1B_BACKWARD, 0);
        pwm_set_gpio_level(MOTOR_1B_PWM, DEFAULT_PWM_LEVEL);
    }
    
}

static void read_DC(uint16_t last) {
    last = adc_read();
    context.mem[254] = (uint8_t)(last >> 8);
    context.mem[255] = (uint8_t)(last & 0xFF);
    //sleep_ms(500);
}
/*  251: bool flag - use custom settings or not 
    252: int num - how many points to devide
    253: time in ms - how long to count
*/
static void read_average_DC(uint16_t last) {
    int N = 10; //how many points
    uint32_t dt = 1; //how long should wait
    if (context.mem[251] == 0x01) {
        N = (int)context.mem[252]; //how many points
        dt =(uint32_t)(context.mem[253]/N); //how long should wait
    } 
    uint32_t sum = 0;
    
    for (int i=0;i<N;i++) {
        last = adc_read();
        sum+=(uint32_t)last;
        sleep_ms(dt);
    }
    last =(uint16_t) (sum / N);
    context.mem[254] = (uint8_t)(last >> 8);
    context.mem[255] = (uint8_t)(last & 0xFF);
    //sleep_ms(500);
}

static void blink(int use_blink) {
    
    if (use_blink > 0x00) {
        gpio_put(LED_PIN, 0);
        sleep_ms(500);
        gpio_put(LED_PIN, 1);
        sleep_ms(500);  }
    // } else if (use_blink >= 0x01) {
    //     gpio_put(LED_PIN, 0);
    //     sleep_ms(200);
    //     gpio_put(LED_PIN, 1);
    //     sleep_ms(200); 
    // } else if (use_blink == 0x00) {
    //     gpio_put(LED_PIN, 0);
    //     sleep_ms(2000);
    //     gpio_put(LED_PIN, 1);
    //     sleep_ms(2000); 
    // }
          
    
}



int main() {
    stdio_init_all();
    //init_LED();
    init_DC();
    //init_PWM();
    init_MOTORS();
    setup_slave();
    uint16_t last;
    while (1) {
        read_average_DC(last);
        use_motors();
        //sleep_ms(10);
    }
    // while (1) {
    //     blink(context.mem[1]);
    //     context.mem[255]+=1;
    // }

}
