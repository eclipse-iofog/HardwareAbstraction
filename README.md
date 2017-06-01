# HAL
HAL stands for Hardware Abstraction Layer. It's REST/WS abstraction for hardware capabilities for Linux based machines.
 
> ##### Prerequisites:
> container needs to be run with next options to grant access: 
> <pre>--net=host --privileged</pre>
 
### REST
REST server listens on port 54331. 

#### LSCPU info (GET)
 Returns parsed info of 'lscpu' command
 <pre> http://localhost:54331/hal/hwc/lscpu </pre>
 Response example
 <pre></pre>
#### LSPCI info (GET)
 Returns parsed info of 'lspci' command
 <pre> http://localhost:54331/hal/hwc/lspci </pre>
 Response example
 <pre></pre>
#### LSUSB info (GET)
 Returns parsed info of 'lsusb' command
 <pre> http://localhost:54331/hal/hwc/lsusb </pre>
 Response example
 <pre></pre>
#### LSHW info (GET)
 Returns parsed info of 'lscpu' command
 <pre> http://localhost:54331/hal/hwc/lshw </pre>
 Response example
 <pre></pre>
#### CPU info (GET)
 Returns parsed info from file /proc/cpuinfo
 <pre> http://localhost:54331/hal/hwc/proc/cpuinfo </pre>
 Response example
 <pre></pre>
#### USB devices list (GET)
 Returns a list of serial ports
 <pre> http://localhost:54331/hal/rs232/list </pre>
 Response example
 <pre></pre>
 
### WebSockets
WS server listens on port 54332. 



