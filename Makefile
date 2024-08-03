CC=gcc 
CFLAGS=-Wall -Wextra -std=c11 
TARGET=main

$(TARGET): main.o
	$(CC) $(CFLAGS) -o $(TARGET) main.o

main.o: main.c 
	$(CC) $(CFLAGS) -c main.c 

main.s: main.c 
	$(CC) $(CFLAGS) -S main.c 

clean:
	rm -rf $(TARGET) *.o *.s *.asm *.exe 

.PHONY: clean asm 

asm: main.s
