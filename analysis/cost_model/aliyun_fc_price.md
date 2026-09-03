函数计算 GPU 实例没有单一的“单价”，而是按 **CU 使用量**统一计费，不同 GPU 系列和状态（活跃/浅休眠）通过 CU 转换系数折算后，再乘以 CU 阶梯单价。

### CU 阶梯单价
| 阶梯 | CU 使用量范围 | 单价 |
| :--- | :--- | :--- |
| 阶梯1 | (0, 1亿] | 0.00012 元/CU |
| 阶梯2 | (1亿, 5亿] | 0.00010 元/CU |
| 阶梯3 | >5亿 | 0.00008 元/CU |

以上为官网标准单价，价格可能调整，请以控制台或官网实时显示为准。

### GPU 使用量的 CU 转换系数
GPU 资源使用量需先按以下系数转换为 CU，再套用上述阶梯单价：

| GPU 系列 | 活跃状态转换系数 | 浅休眠状态转换系数 |
| :--- | :--- | :--- |
| Tesla 系列 | 2.1 CU/(GB*秒) | 0.5 CU/(GB*秒) |
| Ampere 系列 | 1.8 CU/(GB*秒) | 0.3 CU/(GB*秒) |
| Ada 系列 (ada.1) | 1.7 CU/(GB*秒) | 0.2 CU/(GB*秒) |
| Ada 系列 (ada.2/ada.3) | 1.95 CU/(GB*秒) | 0.23 CU/(GB*秒) |
| Blackwell 系列 | 2.1 CU/(GB*秒) | 0.28 CU/(GB*秒) |
| Hopper 系列 | 2.31 CU/(GB*秒) | 0.315 CU/(GB*秒) |
| XPU 系列 | 1.2 CU/(GB*秒) | 0.23 CU/(GB*秒) |

此外，GPU 函数运行时还会产生 vCPU、内存、磁盘及函数调用次数的费用，这些资源也有各自的 CU 转换系数。具体费用可通过函数计算价格计算器测算，实际账单以控制台为准。 

相关链接 
准实时推理场景 https://help.aliyun.com/zh/functioncompute/quasi-real-time-inference-scenarios
新增浅休眠GPU计费项及启用方式 https://help.aliyun.com/zh/functioncompute/fc/product-overview/the-idle-gpu-usage-billable-item-is-added-to-function-compute
函数计算资源计费与前置准备说明 https://help.aliyun.com/zh/functioncompute/fc/use-cases/two-ways-to-quickly-deploy-qwq-32b-reasoning-model
GPU 实例正式商业化_函数计算 https://www.aliyun.com/product/news/22314
计费概述 https://help.aliyun.com/zh/functioncompute/billing-overview-of-fc
产品计费FAQ https://help.aliyun.com/zh/functioncompute/faq-about-billing
函数计算助力领健信息为“看牙”注入AI活力_医疗健康_阿里云客户案例 https://www.aliyun.com/customer-stories/health-care-2024-linkedcare
实时推理成本计算与弹性伸缩问题解答 https://help.aliyun.com/zh/functioncompute/fc/real-time-inference-scenarios-1
阿里云Serverless服务助力Rokid人机交互平台实现降本增效_人工智能_阿里云客户案例 https://www.aliyun.com/customer-stories/ai-2024-rokid
计费项统一为CU使用量及优惠活动说明 https://help.aliyun.com/zh/functioncompute/fc/product-overview/product-changes-changes-of-billable-items-resource-plans-and-trial-quota-of-function-compute
年中加速季，算力全配齐 https://www.aliyun.com/daily-act/ecs/activity_selection
GPU云服务器计费 https://help.aliyun.com/zh/egs/billing-2
什么是GPU云服务器 https://help.aliyun.com/zh/egs/what-is-elastic-gpu-service
计费常见问题 https://help.aliyun.com/zh/pai/faq-about-billing
