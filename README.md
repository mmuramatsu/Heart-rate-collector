# Heart Rate Collector

This repository contains the source code of a heart rate and RR-intervals collector from a Polar H10 sensor.

## Installation / Prerequisites

#### User installation

Just clone this repository

    $ git clone https://github.com/mmuramatsu/Heart-rate-collector.git

#### Dependencies

**Heart rate collector** requires the following:

- Python (>=3.12.0)
- pandas >= 2.0.3
- numpy >= 1.24.4
- bleak >= 0.22.3
- matplotlib >= 3.7.5
- PyQt5 >= 5.15.11
- pynput >= 1.7.7
- scikit-learn >= 1.3.2
- hrv-analysis >= 1.0.5
- astropy < 6.0.0

To install all dependencies, run this command:

    $ pip install -r requirements.txt

## Getting started

#### Running

Type on terminal:

    $ python app.py
