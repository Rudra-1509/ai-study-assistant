import os
import warnings

# Silence TensorFlow C++ logs
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# Disable oneDNN optimizations (removes CPU feature spam)
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# Prevent transformers from touching TF/JAX
os.environ["TRANSFORMERS_NO_TF"] = "1"
os.environ["TRANSFORMERS_NO_FLAX"] = "1"

# Silence Python warnings
warnings.filterwarnings("ignore")
