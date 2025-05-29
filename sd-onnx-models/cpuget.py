from diffusers import StableDiffusionPipeline
from diffusers.onnx_utils import export_onnx_model

export_onnx_model(
    model_name="Xenova/stable-diffusion-v1-5",
    output_path="./sd-onnx-models/",
    device="cpu"
)
