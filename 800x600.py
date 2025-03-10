from machine import Pin, mem32
import utime
import rp2

# Define the base address of the PIO control register
PIO_BASE = 0x50200000
PIO_CTRL = PIO_BASE + 0x00


@rp2.asm_pio(set_init=(rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW))
def h():
    wrap_target()
    set(pins, 0b10) [19]
    nop()        [19]
    nop()        [19]
    nop()        [19]
    nop()        [19]
    nop()        [19]
    nop()        [19]
    nop()        [19]
    nop()        [19]
    nop()        [19] #200
    set(pins, 0b11) [9]  #210
    set(pins, 0b01) [19] 
    nop()        [11] #242
    set(pins, 0b11) [19] 
    set(pins, 0b11) [0]
    irq(0)  
    wrap()

@rp2.asm_pio(set_init=(rp2.PIO.OUT_HIGH), autopull=True, pull_thresh=32)
def v():
    pull(block)
    wrap_target()
    mov(x, osr)   # Load the OSR (number of cycles) into x
    label("active")
    wait(1,irq,0) 
    #irq(1) [1]
    jmp(x_dec,"active")
    nop()       
    set(pins, 0) [3]
    set(pins, 1) [22]     
    wrap()


sm0 = rp2.StateMachine(0, h, freq=10_000_000, set_base=machine.Pin(16))
sm1 = rp2.StateMachine(1, v, freq=37_878, set_base=machine.Pin(18))
sm1.put(300)

while True:
    # Synchronize both state machines by setting the ctrl register directly
    mem32[PIO_CTRL] |= (1 << 0) | (1 << 1)  # Start sm0 and sm1 simultaneously
