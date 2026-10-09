# Native Metal GPU smoke test

- Scene: `/Users/faputa/Documents/Jilong_Port_Reconstruction/Jilong_Port_2019.blend`
- Blender: installed 5.2.0 Alpha build aba09c21dbc6.
- Requested: Cycles GPU, enabled Apple M5 Metal device, CPU disabled; hero camera; 320 x 213 pixels; 8 samples; denoising.
- Script: `/private/tmp/jilong_gpu_smoke.py`
- Captured log: `/private/tmp/jilong_gpu_smoke.log`
- GPU device detection succeeded: Apple M5 (GPU - 10 cores), METAL.
- Render began at 2026-10-09 22:11:10 Asia/Singapore.
- Result: no output PNG or rendering progress after the authorized ten-minute startup cap. The native `MTLCompilerService` was still consuming approximately 40% CPU. This test did not confirm a successful GPU render.
- Only test Blender PID 10221 was sent SIGTERM after the cap; tracked session 81954 closed with exit code 143. Root rendering processes and project files were not modified.
- Native Metal compiler service PID 10225 remained active immediately after its Blender client ended; it was not manually killed, per the scope limiting termination to the smoke Blender process.
- Interpretation: native shader compilation startup prevented timely validation in this installed alpha build. CPU rendering remains the verified delivery path. This observation does not establish that Metal rendering is universally unsupported.
