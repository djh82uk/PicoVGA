from machine import Pin, mem32
import utime
import rp2
import random

# Define the base address of the PIO control register
PIO_BASE = 0x50200000
PIO_CTRL = PIO_BASE + 0x00



@rp2.asm_pio(set_init=(rp2.PIO.OUT_HIGH), autopull=True, pull_thresh=32)
def h():    
    pull(block)
    wrap_target()
    # Active & FrontPorch
    mov(x, osr)   # Load the OSR (number of cycles) into x
    label("activeporch")
    jmp(x_dec,"activeporch")
    # Sync
    set(pins, 0) [31]
    set(pins, 0) [31]
    set(pins, 0) [31]
    # BackPorch
    set(pins, 1) [31] 
    set(pins, 1) [13]
    irq(0)       
    wrap()

@rp2.asm_pio(sideset_init=(rp2.PIO.OUT_HIGH), autopull=True, pull_thresh=32)
def v():
    pull(block)
    wrap_target()
    # Active
    mov(x, osr)   # Load the OSR (number of cycles) into x
    label("active")
    wait(1,irq,0)
    irq(1) 
    jmp(x_dec,"active")
    # FrontPorch
    set(y, 9)
    label("frontporch")
    wait(1,irq,0)
    jmp(y_dec,"frontporch")
     # Sync
    wait(1,irq,0)  .side(0)
    wait(1,irq,0)
    # BackPorch
    set(y, 31)
    label("backporch")
    wait(1,irq,0)   .side(1)
    jmp(y_dec,"backporch")
    wait(1,irq,0)
    wrap()

@rp2.asm_pio(out_init=(rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW),out_shiftdir=(rp2.PIO.SHIFT_RIGHT), autopull=True, pull_thresh=16)
def img():    
    wrap_target()
    pull
    wait(1,gpio,16)  
    wait(1,gpio,17)
    out(pins,15)  [31]
    nop() [28]
    wrap()

sm0 = rp2.StateMachine(0, h, freq=25_175_000, set_base=machine.Pin(16))
sm1 = rp2.StateMachine(1, v, freq=125_000_000, sideset_base=machine.Pin(17))
sm2 = rp2.StateMachine(2, img, freq=25_175_000, out_base=machine.Pin(0))
sm0.put(655)
sm1.put(480)
# sm2.put(655034035)

# pixelcount = 655034035

while True:
    # Synchronize both state machines by setting the ctrl register directly
    mem32[PIO_CTRL] |= (1 << 0) | (1 << 1) | (1 << 2)  # Start sm0 and sm1 simultaneously
    # pixelcount = pixelcount -2
    # sm2.put(64511)
    sm2.put(random.randint(0,65536))

