#!/bin/sh
# Estado del render del show: últimas líneas del log.
tail -n 12 "$(dirname "$0")/../../renders/render_show.log"
