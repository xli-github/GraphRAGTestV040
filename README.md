# 1、GraphRAG介绍
就在两天前(2024.11.5) GraphRAG 发布了 0.4.0版本，该版本的代码经过一轮重构后，已于之前的代码结构有了很大的不同             
该版本引入了增量更新索引和DRIFT图推理搜索查询(一种混合本地与全局的搜索的方法)                               

## 1.1 定义
GraphRAG是微软研究院开发的一种创新型检索增强生成（RAG）方法，旨在提高大语言模型LLM在处理复杂信息和私有数据集时的推理能力                             
GraphRAG 是一种基于大型语言模型 (LLM) 的技术，用于从非结构化文本文档中生成知识图谱和摘要，并利用这些内容提升在私有数据集上的检索增强生成 (RAG) 效果                      
通过 GraphRAG，用户能够从大量非结构化的文本数据中提取信息，构建一个全局概览，同时还可以深入挖掘更为本地化的细节              
该系统借助 LLM 生成知识图谱，识别文档中的实体和关系，利用数据的语义结构响应复杂查询                  
微软正在进一步拓展此技术，开发出一种全新方法：DRIFT 搜索（动态推理与灵活遍历）                                             

## 1.2 索引 indexing 
是一个数据管道和转换套件，旨在利用LLM从非结构化文本中提取有意义的结构化数据    
核心功能：    
**[1]** 从原始文本中提取实体、关系和声明    
**[2]** 在实体中执行社区检测    
**[3]** 生成多级粒度的社群摘要和报告     
**[4]** 将实体嵌入图向量空间     
**[5]** 将文本块嵌入文本向量空间     
**[6]** 管道的输出可以json和parquet等多种格式存储      
提供的实体类型：   
**[1]** Document：输入的文档，csv或txt中的单个行     
**[2]** TextUnit：要分析的文本块，Document与TextUnit关系为1:N关系         
**[3]** Entity：从TextUnit中提取的实体         
**[4]** Relationship：两个实体之间的关系，关系由Covariate（协变量）生成        
**[5]** Covariate：协变量，提取声明信息，包含实体的声明       
**[6]** CommunityReport：社群报告，实体生成后对其执行分层社群检测，并为该分层中的每个社群生成报告        
**[7]** Node：节点，实体和文档渲染图的布局信息           

## 1.3 提示微调 prompt tuning
为生成的知识图谱创建领域自适应prompt模版的功能，提供两种方式进行调整：      
**自动调整：** 通过加载输入，将输入分割成文本块，然后运行一系列LLM调用和prompt模版替换来生成最终的prompt模版     
**手动调整：** 手动调整prompt模版             
根据实际情况选择相关参数：           
**--config** :(必选) 所使用的配置文件，这里选择setting.yaml文件     
**--root** :(可选)数据项目根目录，包括配置文件（YML、JSON 或 .env）。默认为当前目录       
**--domain** :(可选)与输入数据相关的域，如 “空间科学”、“微生物学 ”或 “环境新闻”。如果留空，域将从输入数据中推断出来     
**--method** :(可选)选择文档的方法。选项包括全部(all)、随机(random)或顶部(top)。默认为随机       
**--limit** :(可选)使用随机或顶部选择时加载文本单位的限制。默认为 15     
**--language** :(可选)用于处理输入的语言。如果与输入语言不同，LLM 将进行翻译。默认值为“”，表示将从输入中自动检测     
**--max-tokens** :(可选)生成提示符的最大token数。默认值为 2000     
**--chunk-size** :(可选)从输入文档生成文本单元时使用的标记大小。默认值为 20           
**--output** :(可选)保存生成的提示信息的文件夹。默认为 “prompts”          

## 1.4 检索 query
本地搜索（Local Search）、全局搜索（Global Search）、问题生成（Question Generation）       
**本地搜索（Local Search）：基于实体的推理**     
本地搜索方法将知识图谱中的结构化数据与输入文档中的非结构化数据结合起来，在查询时用相关实体信息增强 LLM 上下文    
这种方法非常适合回答需要了解输入文档中提到的特定实体的问题（例如，"洋甘菊有哪些治疗功效？）        
**全局搜索（Global Search）： 基于全数据集推理**       
根据LLM生成的知识图谱结构能知道整个数据集的结构（以及主题）     
这样就可以将私有数据集组织成有意义的语义集群，并预先加以总结。LLM在响应用户查询时会使用这些聚类来总结这些主题    
**DRIFT搜索（DRIFT Search）:动态推理与灵活遍历**                          
DRIFT 搜索通过整合社区信息，使本地搜索的起点更为宽泛，能够检索更多类型的事实，从而提升查询的详细性            
DRIFT 在 GraphRAG 的查询引擎基础上进一步扩展，为本地搜索提供了更精细的分层查询方式，使其能够处理与预定义模板不完全匹配的复杂查询                        
**问题生成（Question Generation）：基于实体的问题生成**        
将知识图谱中的结构化数据与输入文档中的非结构化数据相结合，生成与特定实体相关的候选问题       


# 2、前期准备工作
## 2.1 开发环境搭建:anaconda、pycharm
anaconda:提供python虚拟环境，官网下载对应系统版本的安装包安装即可                                      
pycharm:提供集成开发环境，官网下载社区版本安装包安装即可                                               
可参考如下视频进行安装，【大模型应用开发基础】集成开发环境搭建Anaconda+PyCharm                                                          
https://www.bilibili.com/video/BV1q9HxeEEtT/?vd_source=30acb5331e4f5739ebbad50f7cc6b949                             
https://youtu.be/myVgyitFzrA          

## 2.2 大模型相关配置
(1)GPT大模型使用方案              
(2)非GPT大模型(国产大模型)使用方案(OneAPI安装、部署、创建渠道和令牌)                 
(3)本地开源大模型使用方案(Ollama安装、启动、下载大模型)                         
可参考如下视频:                         
提供一种LLM集成解决方案，一份代码支持快速同时支持gpt大模型、国产大模型(通义千问、文心一言、百度千帆、讯飞星火等)、本地开源大模型(Ollama)                       
https://www.bilibili.com/video/BV12PCmYZEDt/?vd_source=30acb5331e4f5739ebbad50f7cc6b949                 
https://youtu.be/CgZsdK43tcY           


# 3、项目初始化
## 3.1 下载源码
GitHub或Gitee中下载工程文件到本地，下载地址如下：                
https://github.com/NanGePlus/GraphRAGTestV040                                                           
https://gitee.com/NanGePlus/GraphRAGTestV040                                    

## 3.2 构建项目
使用pycharm构建一个项目，为项目配置虚拟python环境               
项目名称：GraphRAGTestV040                                   

## 3.3 将相关代码拷贝到项目工程中           
直接将下载的文件夹中的文件拷贝到新建的项目目录中               

## 3.4 安装项目依赖          
命令行终端中执行如下命令安装依赖包                                           
pip install -r requirements.txt            
每个软件包后面都指定了本次视频测试中固定的版本号           
**注意:** 截止2024.11.8，本项目graphrag最新版本0.4.0，建议先使用要求的对应版本进行本项目测试，避免因版本升级造成的代码不兼容。测试通过后，可进行升级测试                    


# 4、项目测试
## 4.1 首次构建GraphRAG索引
### (1)创建所需文件夹          
在当前项目下创建个文件夹，**注意:** 这里的ragtest文件夹为自定义文件夹，下面所有操作均在该文件夹目录下进行操作         
mkdir -p ./ragtest          
cd ragtest     
mkdir -p ./input           
### (2)准备测试文档
**注意:** 这里以西游记白话文前九回内容为例，先将other/text/下的1-6.txt文件直接放入ragtest/input文件夹下           
### (3)初始化           
graphrag init --root ./                         
### (4)参数配置
初始化完成后，设置.env和settings.yaml,具体参考提供的other/temp下的.env和settings.yaml文件内容，直接拷贝即可                                 
### (5)优化提示词     
python -m graphrag prompt-tune --config ./settings.yaml --root ./ --language Chinese --output ./prompts                           
### (6)构建索引
graphrag index --root ./                       
### (7)测试
graphrag query --root ./ --method global --query "这个故事的主题是什么?"                              
graphrag query --root ./ --method local --query "谁是唐僧，他的主要关系是什么?"            
graphrag query --root ./ --method drift --query "谁是唐僧，他的主要关系是什么?"                

## 4.2 知识图谱使用neo4j图数据库进行可视化
### (1)配置数据库
首先需要进入neo4j数据库网站，使用云服务版本，这里直接打开neo4j平台，注册成功后创建实例即可                        
https://console-preview.neo4j.io/tools/query                       
### (2)运行脚本 python neo4jTest.py  
测试代码在utils文件夹，将other/utils文件夹直接拷贝到ragtest文件夹下                      
打开neo4jTest.py代码根据自己的实际情况进行调整                              
**修改文件所在路径，替换为你的对应工程的文件路径**                                
GRAPHRAG_FOLDER="/Users/janetjiang/Desktop/agi_code/GraphRAGTestV040/ragtest/output"                 
**配置自己的neo4j的数据库连接信息**           
NEO4J_URI="neo4j+s://7febbfaf.databases.neo4j.io"          
NEO4J_USERNAME="neo4j"            
NEO4J_PASSWORD="JNv34Wd3g0yeIdq23HvrlKscJP-454rNpKlYscaqmKE"              
NEO4J_DATABASE="neo4j"                  
## (3)可视化查询
脚本运行成功后，打开数据库进行查询     
MATCH (n:`__Entity__`)          
WHERE n.name CONTAINS '唐僧'                
RETURN n LIMIT 25;               
MATCH (n:`__Entity__`)                 
WHERE n.name CONTAINS '八戒'                  
RETURN n LIMIT 25;                   

## 4.3 增量更新索引
### (1)准备增量测试文档
将原ragtest/input文件夹下1-6.txt文件删除            
然后，继续使用西游记白话文，选择7-9回，将other/text/下的7-9.txt文件直接放入ragtest/input文件夹下               
### (2)修改参数配置
修改settings.yaml文件内容，进行增量索引构建，则开启该参数设置                            
update_index_storage:                             
    type: file                                     
    base_dir: "update_output"               
### (3)构建索引
graphrag index --root ./                   
### (4)知识图谱可视化
打开neo4jTest.py代码根据自己的实际情况进行调整,修改文件所在路径为存储增量数据的文件路径                                            
GRAPHRAG_FOLDER="/Users/janetjiang/Desktop/agi_code/GraphRAGTestV040/ragtest/update_output"            
修改完成后，重复步骤4.2进行可视化查询验证，脚本运行成功后，打开数据库进行查询              
MATCH (n:`__Entity__`)          
WHERE n.name CONTAINS '唐僧'                
RETURN n LIMIT 25;               
MATCH (n:`__Entity__`)                 
WHERE n.name CONTAINS '八戒'                  
RETURN n LIMIT 25;                  
              
