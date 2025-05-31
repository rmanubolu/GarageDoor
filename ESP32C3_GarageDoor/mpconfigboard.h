// This configuration is for a generic ESP32C3 board with 4MiB (or more) of flash.

#define MICROPY_HW_BOARD_NAME               "ESP32C3 module"
#define MICROPY_HW_MCU_NAME                 "ESP32C3"

// Enable UART REPL for modules that have an external USB-UART and don't use native USB.
#define MICROPY_HW_ENABLE_UART_REPL         (1)

#define MICROPY_HW_I2C0_SCL                 (5)
#define MICROPY_HW_I2C0_SDA                 (4)

#define MICROPY_HW_SPI1_MOSI                (7)
#define MICROPY_HW_SPI1_MISO                (2)
#define MICROPY_HW_SPI1_SCK                 (6)

