# Frequency Resolved Optical Gating

Frequency Resolved Optical Gating (FROG) is a technique for measuring the spectral phase of ultrashort laser pulses. The technique was invented by Rick Trebino and Daniel J. Kane in 1991. Initially, it was thought that in order to measure an event in time, a shorted event was needed, with which to measure it. Since the ultrashort pulses are the shortest events ever created, it was assumed that their complete measurement in time was impossible. The FROG, however, was the first method to solve this problem by measuring the spectrogram of the pulse, in which the pulse gates itself in a non-linear optical medium. The resulting gated part of the pulse is then spectrally resolved as a function of the delay between the two pulses. Finally, the retrieval of the pulse from the corresponding FROG trace is performed using a two-dimensional phase-retrieval algorithm (whose roots lie in the Fundamental Theorem of Algebra)[[1]]. 

In this project, I have built a GUI-based software for Second Harmonic Generation-Frequency Resolved Optical Gating (SHG-FROG), which along with the necessary optical elements, is used to obtain a FROG trace. The retrieval is carried out using the free FROG Code developed by Trebino group at Georgia Tech, which takes the measured FROG trace collected in the previous step and retrives the pulse intensity and phase in both temporal and spectral domains. This respository does not contain the Trebino phase-retrieval code, but it can be downloaded [here][2].    

## Devices Required

In order to collect the FROG trace using this software, you need to have the following devices:
* The FROG optical setup - A diagram is given [here][3]. 
* [StellarNet BLUE-Wave Miniature Spectrometer][4] 
* [Newport 3-Axis Motion Controller and Driver][5] (Model: ESP 300/301) 
* [Newport Motorized Linear Stage, Miniature, 25 mm Travel, Stepper Motor][6] (Model: MFA-PPD)


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```
Give examples
```

### Installing

A step by step series of examples that tell you how to get a development env running

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system




## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments


[1]: https://link.springer.com/book/10.1007%2F978-1-4615-1181-6
[2]: https://onedrive.live.com/?authkey=%21AOtakabqcXVfiOw&id=651160A0FAB1C3EF%21462&cid=651160A0FAB1C3EF
[3]: https://en.wikipedia.org/wiki/Frequency-resolved_optical_gating#/media/File:SHG_FROG.png
[4]: https://www.stellarnet.us/wp-content/uploads/StellarNet-BLUE-Wave-SPEC.pdf
[5]: https://www.newport.com/f/esp301-3-axis-dc-and-stepper-motion-controller?q=esp300:relevance:isObsolete:false:npCategory:esp301-3-axis-dc-%26-stepper-motion-controller
[6]: https://www.newport.com/p/MFA-PPD



