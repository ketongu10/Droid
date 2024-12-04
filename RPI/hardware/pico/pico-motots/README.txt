INSTRUCTION FOR DOLBOJOB

to reload software on pico you should do this:
1) find smth like sda1
ls /dev
2) mount it
sudo mount /dev/sda1 /mnt/pico
3) move to pico-motors/build and remove old files
rm -r *
4) cmake .. && make -j4 && load_pico test.uf2
5) to check i2c 
i2cdump -y 1 0x17
6) to change value in buffer //device addres/byte addres/value//
 i2cset -y 1 0x17 0x01 0x02
7) same can be done with python
accel.py