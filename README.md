# LRB on memory access traces

## Setup
First step is to get access to the leap0x machines from Shaurya.

### Parsec
Use the unofficial fork from here: [https://github.com/cirosantilli/parsec-benchmark](https://github.com/cirosantilli/parsec-benchmark). I could not get other versions to work. You can also follow the instructions on their README (we only need `canneal`).

```bash
cd parsec-benchmark/
./configure
. env.sh
cd ..
parsecmgmt -a build -p canneal
```

### PINtool
The version that works with the adapted code is 3.26:
```bash
wget https://software.intel.com/sites/landingpage/pintool/downloads/pin-3.26-98690-g1fc9d60e6-gcc-linux.tar.gz
tar -xvf pin-3.26-98690-g1fc9d60e6-gcc-linux.tar.gz
mv pin-3.26-98690-g1fc9d60e6-gcc-linux.tar.gz pintool
```

Then, update the reporting file in `pinatrace.cpp` to use the one in this repo:
```bash
mv ./lrb_pointer/pinatrace.cpp ./pintool/source/tools/ManualExamples/pinatrace.cpp
cd ./pintool/source/tools/ManualExamples
make obj-intel64/pinatrace.so
cd
```

### LRB
Follow the instructions in [INSTALL.md](https://github.com/kdchin/lrb/blob/kyle/working/INSTALL.md).
Note that this has some changes from the original LRB repo to make it install correctly.

```bash
git clone --recurse-submodules git@github.com:kdchin/lrb.git webcachesim
cd webcachesim
./scripts/install.sh
# test (note that this path is corrected from the original)
./build/bin/webcachesim_cli
#output: webcachesim_cli traceFile cacheType cacheSize [--param=value]
```
 They may not work, in which case you can try to adapt the code as such:
- Fix the `SIGSTKSZ` constant error for mongo by replacing it with a constant integer:
    - https://src.fedoraproject.org/rpms/R-testthat/blob/rawhide/f/R-testthat-sigstksz-not-constant.patch

## Setup PIN
Setup pin as a subfolder inside the pointer analysis folder. Follow build instructions from [here](https://software.intel.com/sites/landingpage/pintool/docs/98484/Pin/html/index.html).
Make sure you can build and setup the [pinatrace](https://software.intel.com/sites/landingpage/pintool/docs/98484/Pin/html/index.html#MAddressTrace) example located in Manual Examples for PIN.
<!-- https://www.intel.com/content/www/us/en/developer/articles/tool/pin-a-binary-instrumentation-tool-downloads.html -->

Copy the updated pinatrace tool to the Manual Examples folder from the repository to the PIN sub directory. 

The build command for x86-64 architectures is ``` make arch=intel64 ```

## Collecting memory traces
We use cgroups to control the memory percentage available to an application. Use the same percentage you would as without PIN tool.
Pin commands look different for different applications. 

To setup the cgroups first:
```bash
sudo cgcreate -g memory:trial
```

For microbenchmarks use the following command:
```bash
sudo cgexec -g memory:trial ./pintool/pin -t ./pintool/source/tools/ManualExamples/obj-intel64/pinatrace.so -- ./benchmark_to_run 2>&1 1>output
```

### Parsec traces
Once parsec is set up from earlier, you can run this. For parsec we use the -s option of the benchmark to append a command to run before the benchmark. 

```bash
sudo parsecmgmt -a run -p parsec.canneal -i simsmall -s "sudo cgexec -g memory:trial /home/kyle/pintool/pin -t /home/kyle/pintool/source/tools/ManualExamples/obj-intel64/pinatrace.so --" > /data1/kyle/simsmall_output.tr
```
sudo parsecmgmt -a run -p parsec.canneal -i simmedium -s "sudo cgexec -g memory:trial /home/kyle/pintool/pin -t /home/kyle/pintool/source/tools/ManualExamples/obj-intel64/pinatrace.so --" > /data1/kyle/simmedium_output.tr

You will need to give absolute paths (i.e. substitute your username in `/home/kyle/`) and also create a `/data1/<username>` folder to pipe the results into, to avoid running out of disk space. You may also have to run this as root using `sudo su` and then re-sourcing `parsecmgmt`.

<!-- ### xhpcg and mpi traces
Setup xhpcg from [here](https://hpcg-benchmark.org/software/browse.html%3Fstart=0&per=5.html). Follow [these instructions](https://ireneli.eu/2016/02/15/installation/) to setup MPI first.
Run xhpcg with PIN.

```bash
sudo cgexec -g memory:trial mpirun --allow-run-as-root -np 1 ./pintool/pin -t ./pint/source/tools/ManualExamples/obj-intel64/pinatrace.so -- ./hpcg/bin/xhpcg 32 24 16 2>&1 1>mpi_output
``` -->

## Running LRB on the traces
The parameters I chose for canneal simsmall were:
- CacheSize = 22020096 (21mb)
- BeladyBoundary = 174762
- MemoryWindow = 174762
- batch_size = 32768

#### Collecting the traces
This is repeated from below
```bash
sudo parsecmgmt -a run -p parsec.canneal -i simsmall -s "sudo cgexec -g memory:trial /home/kyle/pintool/pin -t /home/kyle/pintool/source/tools/ManualExamples/obj-intel64/pinatrace.so --" > /data1/kyle/simsmall_output.tr
```
The trace output may got to `./parsec-benchmark/pkgs/kernels/canneal/run/pinatrace.out` instead, in which case you should move it to the proper location.

#### Formatting the traces
This formats the pinatrace into the trace file format for lrb
```bash
    python3 format_trace.py <pinatrace.out> <lrb_trace.tr>
```

### Simulate LRU on the trace and report statistics
```bash
    python3 dataset_qualities.py <lrb_trace.tr> cache_size belady_boundary
```

#### Simulating LRB on the trace
```bash
WEBCACHESIM_TRACE_DIR=/data1/kyle ./webcachesim/build/bin/webcachesim_cli lrb_trace.tr LRB 22020096 --memory_window=174762 --belady_boundary=174762 --batch_size=32768 > /data1/kyle/lrb_small.out
```

### View output of LRB simulation
```bash
    python3 reveal_output.py <lrb_small.out>
```