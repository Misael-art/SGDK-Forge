# Route comparison matrix

Stage 1 is geometry-only and has claim ceiling `mechanical_geometry_probe`. No automatic winner is declared.

| route | tool | algorithm | status | raw SHA-256 |
|---|---|---|---|---|
| im_nearest | ImageMagick | Point | passed | cc712a399d83c5777699b139ee12bd8fbde67916f99094cf2e7cb6d2bb33b70d |
| im_box_area | ImageMagick | Box | passed | a5cfc5d36b2b5b113149eec171a8da185c1f445af03b645a8e1f7ae8be21c66c |
| im_bilinear_triangle | ImageMagick | Triangle | passed | 9165cbe1b5fe0f433d2bc2f760fc22ae032a611b0b048d7251dbcc77f22efd0c |
| im_bicubic | ImageMagick | Cubic | passed | 193a92398ec85ef61d84628cfe359d04ef91b81facdd3b3ac9db7f5facdfdbe9 |
| im_lanczos2 | ImageMagick | Lanczos2 | passed | cb642b740bfb0237ca0afb8c47e2971b8faa4a314c0033fe5e4344bd77ba3c74 |
| im_lanczos3 | ImageMagick | Lanczos | passed | 933caee8829970d0f8877712396b19b57e5843ef73481aceb047cf338cde72be |
| im_mitchell_netravali | ImageMagick | Mitchell | passed | ee524888bd0be4e146a3236a9480565772b8fa8e752818bf2c9717bf702b17b5 |
| im_catmull_rom | ImageMagick | Catrom | passed | 169426ebbf40eb01631154610cd73fff959afde8540dfa5943c3528225b20cd5 |
| im_b_spline | ImageMagick | Spline | passed | 193a92398ec85ef61d84628cfe359d04ef91b81facdd3b3ac9db7f5facdfdbe9 |
| pil_nearest | Pillow | NEAREST | passed | cc712a399d83c5777699b139ee12bd8fbde67916f99094cf2e7cb6d2bb33b70d |
| pil_box | Pillow | BOX | passed | bfe76cb614764f7f99468185ece934ae3f7d7f20a7098d591274d791d2dd386d |
| pil_bilinear | Pillow | BILINEAR | passed | 8e9a0e085a63c18760fa2bc6cfdedac2fd405b74999e5ca5249174ec4fa73329 |
| pil_hamming | Pillow | HAMMING | passed | fb94872bfb097e49e5c2502fcada4837c676cedb05685fea7f4eefba8f2260b1 |
| pil_bicubic | Pillow | BICUBIC | passed | 483e92562c5978487d37d6a939c1cacb7a73e1d0adaf366db9427df280c88bdf |
| pil_lanczos | Pillow | LANCZOS | passed | fa29d789229d8932a11189b5acf6f50c7e580043f80bf27071d60ff8f0a70fdd |
| cv_nearest | OpenCV | nearest | passed | 44ecc3492da7da48ed2280ed4e488377a32cd795f5b1fa27d4eea5c909946d44 |
| cv_area | OpenCV | area | passed | 9002496f1a3ae404dbafba14a848f4cbb96f37072fbba2d327bc69e616a215bd |
| cv_linear | OpenCV | linear | passed | 381bd003fbd842f3db3715c2f592b58b99bcf863d5eb789b6bae3cea3b6348ed |
| cv_cubic | OpenCV | cubic | passed | 107c4dd25d8dcc3353d8a358d69f19fc3fde68e13d4e16322dc2a83a9e128cfe |
| cv_lanczos4 | OpenCV | lanczos4 | passed | 03e23675876671cc5630ee9ef694dccc31e9326db262d3cfdbd44b48327f3e37 |
| gimp_none | GIMP Console | none | skipped | none |
| gimp_linear | GIMP Console | linear | skipped | none |
| gimp_cubic | GIMP Console | cubic | skipped | none |
| gimp_nohalo | GIMP Console | nohalo | skipped | none |
| gimp_lohalo | GIMP Console | lohalo | skipped | none |

GIMP batch attempts timed out without a deterministic export and are `skipped`; they do not block the matrix.
