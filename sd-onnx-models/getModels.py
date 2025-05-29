from huggingface_hub import hf_hub_download
import shutil
import os

repo_id = "tlwu/stable-diffusion-v1-5-onnxruntime"
model_files = {
    "text_encoder.onnx": "text_encoder/model.onnx",
    "unet.onnx": "unet/model.onnx",
    "vae_decoder.onnx": "vae_decoder/model.onnx"
}

print("📦 Downloading Stable Diffusion ONNXRuntime files from tlwu...")

for out_name, hf_filename in model_files.items():
    path = hf_hub_download(repo_id=repo_id, filename=hf_filename)
    shutil.copy(path, out_name)
    print(f"✅ Downloaded {out_name}")
