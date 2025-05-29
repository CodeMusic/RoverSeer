import argparse
from diffusers import StableDiffusionPipeline
from diffusers.onnx_utils import export_onnx_model

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, required=True)
    parser.add_argument("--output_path", type=str, required=True)
    parser.add_argument("--opset", type=int, default=14)
    args = parser.parse_args()

    pipe = StableDiffusionPipeline.from_pretrained(
        args.model_name,
        use_safetensors=True
    )

    print(f"📦 Loaded model: {args.model_name}")
    export_onnx_model(
        pipe,
        args.output_path,
        opset=args.opset,
        device="cpu"
    )
    print(f"✅ Exported ONNX model to: {args.output_path}")

if __name__ == "__main__":
    main()
