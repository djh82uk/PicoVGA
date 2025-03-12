from machine import Pin, mem32
import utime
import rp2

# Define the base address of the PIO control register
PIO_BASE = 0x50200000
PIO_CTRL = PIO_BASE + 0x00


@rp2.asm_pio(set_init=(rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW), autopull=True, pull_thresh=32)
def h():
    pull(block)
    wrap_target()
    mov(x, osr)   # Load the OSR (number of cycles) into x
    label("active")
    jmp(x_dec,"active")
    set(pins, 0b00) [15]
    set(pins, 0b10) [31]
    nop()        [31]
    nop()        [31]
    set(pins, 0b00) [31] 
    set(pins, 0b01) [14]
    irq(0)  
    wrap()

@rp2.asm_pio(set_init=(rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW), autopull=True, pull_thresh=32)
def v():
    pull(block)
    wrap_target()
    mov(x, osr)   # Load the OSR (number of cycles) into x
    label("active")
    wait(1,irq,0) 
    jmp(x_dec,"active")
    set(pins, 0b00) [9]
    set(pins, 0b10) [1]
    set(pins, 0b00)
    nop()        [31] 
    set(pins, 0b01) 
    irq(1)  
    wrap()

@rp2.asm_pio(set_init=(rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW, rp2.PIO.IN_LOW), autopull=True, pull_thresh=32)
def img():
    wrap_target()
    wait(1,pin,0) [0]
    set(pins, 0b01)
    nop()        [31] 
    set(pins, 0b11)
    nop()        [31] 
    set(pins, 0b10)
    nop()        [31] 
    set(pins, 0b00) [31]
    wrap()

sm0 = rp2.StateMachine(0, h, freq=25_175_000, set_base=machine.Pin(16))
sm1 = rp2.StateMachine(1, v, freq=31_468, set_base=machine.Pin(18))
sm2 = rp2.StateMachine(2, img, freq=100_700_000, set_base=machine.Pin(6), in_base=machine.Pin(16))
sm0.put(640)
sm1.put(240)

while True:
    # Synchronize both state machines by setting the ctrl register directly
    mem32[PIO_CTRL] |= (1 << 0) | (1 << 1) | (1 << 2)  # Start sm0 and sm1 simultaneously
