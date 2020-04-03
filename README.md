# Computing effective reproduction number

In this project, I developed a web app to compute daily effective Reproduction Number and deployed this app on a Heroku cloud server.

I implemented the Wallinga-Teunis method (see References 1 and 2 below). I get the case incidence data from Johns Hopkins University (see above). I get the serial interval distribution from the gamma distribution parameters from reference 3 below.

Since the time-step is small here (daily), the estimates of R varies considerably increasing the risk of negative autocorrelation. To mitigate that, I calculate the estimates over a window of 3 days. For details of this method, see reference 1.


## References
[1] Cori A, Ferguson NM, Fraser C, Cauchemez S. A new framework and software to estimate time-varying reproduction numbers during epidemics. American journal of epidemiology. 2013 Nov 1;178(9):1505-12.

[2] Wallinga J, Teunis P. Different epidemic curves for severe acute respiratory syndrome reveal similar impacts of control measures. American Journal of epidemiology. 2004 Sep 15;160(6):509-16.

[3] Du Z, Xu X, Wu Y, Wang L, Cowling BJ, Meyers LA. The serial interval of COVID-19 from publicly reported confirmed cases. medRxiv. 2020 Jan 1.
