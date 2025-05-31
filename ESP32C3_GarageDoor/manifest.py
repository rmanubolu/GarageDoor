include("$(PORT_DIR)/boards/manifest.py")
freeze("modules")

require("cbor2")
require("senml")
require("logging")