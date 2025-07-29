# garnet
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Validate with hassfest](https://github.com/danTapps/garnet/actions/workflows/hassfest-validate.yml/badge.svg)](https://github.com/danTapps/garnet/actions/workflows/hassfest-validate.yml)
[![HACS Action](https://github.com/danTapps/garnet/actions/workflows/hacs-validate.yml/badge.svg)](https://github.com/danTapps/garnet/actions/workflows/hacs-validate.yml)

Garnet SeeLevel II Bluetooth Integration for Home Assistant

## Disclaimer
This integration is provided without any warranty or support by Garnet. I do not take responsibility for any problems it may cause in all cases. Use it at your own risk.

## Installation

### HACS

Follow [this guide](https://hacs.xyz/docs/faq/custom_repositories/) to add this git repository as a custom HACS repository. Then install from HACS as normal.

### Manual Installation

Copy `custom_components/garnet` into your Home Assistant `$HA_HOME/config` directory, then restart Home Assistant.

### Supported devices:

- Garnet SeeLevel II 709-BTP3
- Garnet SeeLevel II 709-BTP7 - *only supporting Grey Tank 1, Fresh Tank 1, Black Tank 1, Grey Tank 2, Fresh Tank 2, LPG1, Black Tank 2 and Voltage for now, in need of data samples for Grey Tank 3*
