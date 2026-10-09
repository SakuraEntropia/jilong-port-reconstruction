# 吉隆口岸国门 · 2019 外观重建

这是中尼吉隆—热索瓦口岸中方热索国门及联检建筑的可编辑 Blender 外景。以 2019 年 8 月两张有日期依据的正面照片为基准，并用后期官方无人机和反面照片核查体量。具体来源和观察依据见 `research/`。

## 打开与编辑

- 主场景：`Jilong_Port_2019.blend`，默认正面相机与日间 Cycles 设置。
- 傍晚版本：`Jilong_Port_2019_Dusk.blend`，艺术化灯光，未声称复原实际夜景。
- `renders/`：正面、斜视、后部、门洞细节、场地鸟瞰及傍晚实渲图；保留体块和材质预览。
- `scripts/`：可重建的 Blender Python 脚本；`checkpoints/` 保留阶段文件。
- `references/`：研究照片；它们没有作为材质贴图或照片投影使用。

模型以米为单位，包含真正的网格体量、通透车行洞口、后退办公体量、四条高窗的两侧翼楼、檐口齿饰、石材分缝、门窗框、铭牌及近似浮雕国徽。桥梁、栏杆、岗亭、太阳能灯、货车、山地、植被和河谷也为三维几何。重复组件采用共享网格，选定对象可用 Make Single User 后独立编辑。倒角仍是可编辑修改器。

材质采用 Principled PBR 节点：石材微颗粒、板块色差、玻璃反射/折射、涂层金属、混凝土粗糙度和地表岩石/植被变化。字体已打包；程序材质不依赖外部位图。研究文档作为 Text 数据块嵌入场景。

## 范围与可信度

正面轮廓、嵌套矩形洞口、窗带节奏、檐口、中文招牌及桥头外观依据照片。建筑约 54 m 高立面宽、21.8 m 最高轮廓、16 m 主体深，均为比例推估，不能作为实测数据。建模的低层翼楼总宽约 70 m。桥宽 12 m 使用报道数据；模型表现约 107 m 可见桥面及桥头连接。完整尺寸登记见 `research/dimensions.md`。

隐藏侧面与后部细节、楼内布局、桥墩和挡土平台、山体/河床及植被分布为推定。背面红字铭牌依后期照片推定，2019 年背面铭牌细节未核实。仅建必要的室内遮挡和结构，未制作完整可用室内空间。小号藏文为近似转写，国徽是近似几何浮雕。外景为历史版本；后期桥梁改造没有混入 2019 基准。所有未验证项见 `research/uncertainties.md`。

## 重建与渲染

在项目根目录执行（可将程序名替换为已安装 Blender 的绝对路径）：

```bash
blender -b --python scripts/build_scene.py -- --phase detail
blender -b checkpoints/02_detailed.blend --python scripts/render_views.py -- --mode final --device CPU
blender -b Jilong_Port_2019.blend --python scripts/validate_scene.py
```

实际使用 Blender 5.2.0 Alpha。该机器的沙箱阻止原生 Metal 检测，需通过正常的原生进程权限启动；CPU 渲染已验证。日志保留了启动失败、API 兼容修正、预览和最终渲染过程。最终质量记录与场景重新打开验证见 `QA.md` 和 `logs/validation.json`。

参考照片的作者、许可证及未解决的许可证元数据差异保留在 `research/source_index.md`，照片没有被当成可自由发布的原创素材。
