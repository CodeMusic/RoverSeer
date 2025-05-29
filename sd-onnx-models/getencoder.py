from diffusers import OnnxStableDiffusionImg2ImgPipeline

pipe = OnnxStableDiffusionImg2ImgPipeline.from_pretrained(
    "tlwu/stable-diffusion-v1-5-onnxruntime",
#    revision="onnx",
    provider="CPUExecutionProvider"
)
