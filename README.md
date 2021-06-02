# ChiaAutoplotter
## Make multi-machine plotting easy!

ChiaAutoplotter is a utility program, made by [CPool.farm](https://www.cpool.farm) team for inner purposes. It is designed to solve next problems:

- Plotting on several machines 
- Transferring of plots to the harvesters via rsync
- Good and easy user interface
- Monitoring of all the processes

### How to use
First, you have to install a [ChiaAutoplotter-Core](https://github.com/cPoolChia/ChiaAutoplotter-Core) to one machine (most likely your home PC). Follow instructions on page of that repo to do it.
Then, on each server, that will be connected to an application, [Chia CLI](https://github.com/Chia-Network/chia-blockchain/wiki/INSTALL) should be installed and `chia init` should be executed.
After that follow installation guide below to install [ChiaAutoplotter-Worker](https://github.com/cPoolChia/ChiaAutoplotter-Worker) on each server. Then, log in to ChiaAutoplotter GUI, go to the "Servers" page, click the green "Add new" button and type in all information about your machine and a worker's port (default 8000). The server will appear in the table and soon it should test it's connection and change the status from "pending" to "connected" of "failed", depending on if the connection was successfull.

### Installation
