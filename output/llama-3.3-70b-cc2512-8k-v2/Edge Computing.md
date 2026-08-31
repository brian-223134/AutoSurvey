# Comprehensive Survey of Edge Computing: Architecture, Applications, and Challenges

## 1 Introduction to Edge Computing

### 1.1 Definition and Evolution of Edge Computing

Edge computing is a novel computing paradigm that extends cloud resources to the edge of the network, enabling data processing and analysis closer to where it is generated [1]. This paradigm has emerged as a response to the proliferation of Internet of Things (IoT) devices, which generate vast amounts of data that require processing and analysis in real-time [2]. The increasing demand for low-latency applications, improved real-time processing, and enhanced security and privacy has driven the development of edge computing, making it an essential component of various applications, including IoT, smart cities, industrial automation, and healthcare [3].

The evolution of edge computing has been influenced by various factors, including advances in computing and storage technologies, improvements in network infrastructure, and the increasing demand for low-latency applications [4]. As a result, edge computing has undergone significant transformations since its inception, with various architectures and frameworks being proposed to support its development. For instance, the fog computing paradigm extends cloud computing to the edge of the network, enabling data processing and analysis closer to where it is generated. Mobile edge computing, on the other hand, focuses on providing cloud-computing capabilities within the radio access network, closer to mobile users [4]. These developments have been driven by the need for reduced latency, improved real-time processing, and enhanced security and privacy [5].

The development of edge computing is expected to continue, driven by the need for low-latency processing and real-time decision-making, particularly in applications such as IoT, smart cities, and industrial automation. The increasing demand for low-latency applications has led to the development of new technologies and architectures, including 5G networks, which provide ultra-low latency and high-bandwidth connectivity. Furthermore, the integration of edge computing with other emerging technologies, such as artificial intelligence (AI) and blockchain, is also expected to drive its development and adoption [6]. As edge computing continues to evolve, it is essential to understand its current state, applications, and challenges, which will be discussed in the following sections.

In summary, edge computing has evolved significantly over the years, driven by the need for low-latency processing, real-time decision-making, and reduced bandwidth usage [7]. The next section will provide a comprehensive overview of the current state of edge computing, including its architecture, applications, and challenges, setting the stage for a detailed discussion of the field.

### 1.2 Scope and Organization of the Survey

This survey on edge computing is designed to provide a comprehensive overview of the current state of the field, including its architecture, applications, and challenges, building on the foundation established in the previous section, which introduced the concept of edge computing, its evolution, and the motivation behind its adoption. The scope of this survey is broad, covering various aspects of edge computing, from its definition and evolution to its applications in different domains, such as IoT, smart cities, industrial automation, healthcare, transportation systems, and gaming. We will also discuss the challenges and open research issues in edge computing, including security, privacy, scalability, resource management, and energy efficiency [8].

The survey is organized into five main sections, each designed to provide a logical flow of information. The first section, which has already been covered, introduced the concept of edge computing, its evolution, and the motivation behind its adoption. The second section, which will be discussed next, delves into the architectural components of edge computing, including edge devices, edge servers, and the cloud, as well as various frameworks and models for edge computing [9]. The third section explores the diverse applications and use cases of edge computing, including IoT, smart cities, industrial automation, healthcare, transportation systems, and gaming [10]. The fourth section discusses the challenges and open research issues in edge computing, including security, privacy, scalability, resource management, and energy efficiency [11]. The final section summarizes the key findings of the survey and discusses the future directions of edge computing, including potential integrations with emerging technologies such as 5G, AI, and blockchain [12].

Throughout this survey, we will provide an overview of the current research in edge computing, highlighting the key findings, challenges, and open issues. We will also discuss the potential applications and benefits of edge computing, as well as its limitations and challenges. The survey will conclude with a discussion of the future directions of edge computing, including potential research areas and applications [13]. By providing a comprehensive overview of the current state of edge computing, this survey aims to provide a valuable resource for researchers, practitioners, and industries interested in this field [14]. 

The organization of this survey is designed to provide a logical flow of information, starting with the introduction to edge computing, followed by its architecture, applications, challenges, and finally, its future directions. Each section is designed to build on the previous one, providing a comprehensive overview of the field. The survey will also include citations to relevant research papers and studies, providing evidence for the claims made and supporting the arguments presented [15]. By following this organization, the survey aims to provide a clear and concise overview of the current state of edge computing, as well as its potential future directions. 

In terms of the topics that will be covered, this survey will include a wide range of subjects related to edge computing, including its definition, evolution, architecture, applications, challenges, and future directions. The survey will also discuss the potential benefits and limitations of edge computing, as well as its potential applications in different domains. The topics will be covered in a logical and organized manner, providing a comprehensive overview of the field [16]. The survey will also include discussions of the current research in edge computing, highlighting the key findings, challenges, and open issues. By providing a comprehensive overview of the current state of edge computing, this survey aims to provide a valuable resource for researchers, practitioners, and industries interested in this field.

## 2 Edge Computing Architecture and Technologies

### 2.1 Architectural Components of Edge Computing

The architectural components of edge computing are crucial in enabling the efficient processing and analysis of data closer to the source. These components include edge devices, edge servers, and the cloud, which work together to provide a seamless and low-latency computing experience. Edge devices, such as smartphones, tablets, and IoT devices, are the primary sources of data in an edge computing environment [1]. These devices generate vast amounts of data, which can be processed and analyzed in real-time using edge computing technologies.

Edge servers, on the other hand, are the backbone of edge computing, providing the necessary computing resources and storage to process and analyze data from edge devices [17]. These servers can be deployed in various locations, such as cell towers, base stations, or even on-premises, to provide low-latency and high-bandwidth access to applications and services. Edge servers can also be used to cache frequently accessed data, reducing the need for data to be transmitted to the cloud or central data centers.

The cloud is also an essential component of edge computing, providing a centralized location for data storage, processing, and analysis [18]. The cloud can be used to process large amounts of data, perform complex analytics, and provide scalability and flexibility to edge computing environments. However, the cloud is often far away from the edge devices, resulting in higher latency and bandwidth requirements. To address this issue, edge computing uses a hierarchical architecture, where data is processed and analyzed at the edge, and only relevant data is transmitted to the cloud for further processing and analysis.

In addition to edge devices, edge servers, and the cloud, other architectural components of edge computing include networking and communication protocols, such as 5G and Wi-Fi [4]. These protocols provide the necessary connectivity and bandwidth to enable low-latency and high-bandwidth communication between edge devices, edge servers, and the cloud. Edge computing also relies on various software frameworks and platforms, such as containerization and orchestration tools, to manage and deploy applications and services [19].

The integration of these architectural components enables edge computing to provide a wide range of benefits, including low latency, high bandwidth, and improved real-time processing and analysis [20]. Edge computing can also provide improved security and privacy, as data is processed and analyzed closer to the source, reducing the risk of data breaches and cyber attacks [5]. Furthermore, edge computing can enable new use cases and applications, such as smart cities, industrial automation, and autonomous vehicles, which require low-latency and high-bandwidth processing and analysis [21].

In conclusion, the architectural components of edge computing, including edge devices, edge servers, and the cloud, are critical in enabling the efficient processing and analysis of data closer to the source. The integration of these components, along with networking and communication protocols, software frameworks, and platforms, provides a wide range of benefits, including low latency, high bandwidth, and improved real-time processing and analysis. As edge computing continues to evolve, it is likely to play an increasingly important role in enabling new use cases and applications, such as smart cities, industrial automation, and autonomous vehicles [22]. This foundation of architectural components will be essential in supporting the development of edge computing frameworks and models, which will be discussed in the next section, including fog computing, mobile edge computing, and cloudlet-based edge computing.

### 2.2 Edge Computing Frameworks and Models

Edge computing frameworks and models are crucial for the efficient deployment and management of edge computing resources, building upon the architectural components discussed earlier. Various frameworks and models have been proposed to support edge computing, including fog computing [23], mobile edge computing [4], and cloudlet-based edge computing [24]. These frameworks and models enable the efficient processing and analysis of data closer to the source, reducing latency and improving real-time processing capabilities. For instance, fog computing [23] is a distributed computing paradigm that extends cloud computing to the edge of the network, providing computing, storage, and networking resources to end-users.

Mobile edge computing [4] is another framework that provides computing resources at the edge of the network, closer to mobile users, enabling the processing of data in real-time and reducing latency. This framework is particularly useful for applications that require low latency and high bandwidth, such as virtual reality and augmented reality. Cloudlet-based edge computing [24] is a framework that uses cloudlets, which are small-scale cloud data centers located at the edge of the network, providing computing, storage, and networking resources to end-users. This framework is also useful for applications that require low latency and high bandwidth, such as online gaming and video streaming.

In addition to these frameworks, various models have been proposed to support edge computing, including the edge-cloud collaboration model [25] and the fog-cloud collaboration model [26]. These models enable the collaboration between edge devices and cloud servers, providing a more efficient and scalable way to process data. The application of these frameworks and models has been demonstrated in various scenarios, including smart cities [3], industrial automation, and healthcare [27], showcasing the potential of edge computing to improve the efficiency and effectiveness of various industries and domains.

The implementation of edge computing frameworks and models relies on various technologies, including containerization [28] and virtualization [29]. These technologies provide a more efficient and scalable way to deploy and manage edge computing resources, ensuring seamless integration with the architectural components of edge computing. By leveraging these frameworks, models, and technologies, edge computing can provide a wide range of benefits, including low latency, high bandwidth, and improved real-time processing and analysis, which will be further discussed in the following section.

## 3 Applications and Use Cases of Edge Computing

### 3.1 Edge Computing in IoT and Smart Cities

Edge computing has been increasingly applied in Internet of Things (IoT) and smart city applications, enabling real-time data processing, reduced latency, and improved decision-making. In IoT, edge computing allows for the processing of data closer to the source, reducing the need for cloud computing and minimizing latency [20]. This is particularly important in applications such as smart traffic management, where real-time data processing is crucial for optimizing traffic flow and reducing congestion [30]. By leveraging edge computing, smart cities can efficiently manage urban infrastructure and services, leading to improved public services and enhanced quality of life.

One of the key areas where edge computing has made a significant impact is in smart energy management, allowing for real-time monitoring and control of energy consumption in buildings and homes [31]. This can lead to significant energy savings and reduced carbon emissions, making cities more sustainable and environmentally friendly. Additionally, edge computing has enabled the development of smart transportation systems, such as intelligent traffic signals and smart parking management [32], which use real-time data from sensors and cameras to optimize traffic flow and reduce congestion.

Edge computing has also been used in various IoT applications, such as industrial automation, healthcare, and environmental monitoring [33]. In industrial automation, edge computing enables real-time monitoring and control of industrial equipment, improving productivity and reducing downtime [34]. In healthcare, edge computing enables the real-time analysis of medical data, improving patient outcomes and reducing healthcare costs [35]. These applications demonstrate the versatility and potential of edge computing in transforming urban landscapes and improving the lives of citizens.

However, the use of edge computing in smart cities has also raised concerns about security and privacy [30]. As edge computing involves the processing of sensitive data in real-time, it is essential to ensure that this data is protected from unauthorized access and cyber threats. To address these concerns, researchers have proposed various security and privacy frameworks for edge computing, such as encryption and access control mechanisms [36]. Furthermore, edge computing in smart cities also faces challenges related to scalability, reliability, and maintainability [37], which must be addressed to ensure the long-term sustainability of these systems.

In conclusion, edge computing has been increasingly applied in IoT and smart city applications, enabling real-time data processing, reduced latency, and improved decision-making. While there are challenges related to security, privacy, scalability, and reliability, researchers have proposed various solutions to address these concerns. As the use of edge computing in smart cities continues to grow, it is essential to ensure that these systems are designed with security, privacy, and scalability in mind to maximize their benefits and minimize their risks [20]. The successful integration of edge computing in smart cities will rely on the ability to balance these competing demands and create a robust, efficient, and sustainable infrastructure for urban development.

### 3.2 Edge Computing in Industrial Automation, Healthcare, and Transportation

Edge computing has numerous applications in various industries, including industrial automation, healthcare, and transportation, which is a natural extension of its use in smart cities and IoT applications. In industrial automation, edge computing enables real-time monitoring and control of equipment, allowing for predictive maintenance and improved overall efficiency [38]. This is particularly important in industries where equipment failure can have significant consequences, such as in mining or manufacturing. By analyzing data from sensors and machines in real-time, edge computing can help identify potential issues before they become major problems, reducing downtime and increasing productivity.

The use of edge computing in industrial automation is closely related to its application in smart cities, where it is used to manage urban infrastructure and services. In both cases, edge computing enables real-time data processing and analysis, allowing for improved decision-making and reduced latency. In healthcare, edge computing is being used to improve patient monitoring and care [39]. For example, edge computing can be used to analyze data from medical devices such as pacemakers or insulin pumps, allowing for real-time monitoring and alerts in case of any issues [40]. This can be particularly important for patients with chronic conditions, where real-time monitoring can help prevent complications and improve outcomes.

In transportation, edge computing is being used to improve safety and efficiency [41]. For example, edge computing can be used to analyze data from sensors and cameras on autonomous vehicles, allowing for real-time object detection and navigation [42]. This can help improve safety by reducing the risk of accidents, and can also help improve efficiency by optimizing traffic flow and reducing congestion. Edge computing can also be used to analyze data from traffic management systems, allowing for real-time monitoring and optimization of traffic signals and routing [43]. The benefits of edge computing in these industries are closely related to its ability to provide real-time processing and analysis of data, which is essential for improving decision-making and reducing latency.

One of the key benefits of edge computing in these industries is its ability to provide real-time processing and analysis of data [44]. This is particularly important in applications where latency can have significant consequences, such as in healthcare or transportation. By processing data at the edge, rather than in the cloud, edge computing can help reduce latency and improve real-time decision-making. Additionally, edge computing can help improve security and privacy by reducing the amount of data that needs to be transmitted to the cloud or other remote locations [45]. The use of edge computing in these industries is expected to continue growing, driven by the increasing demand for real-time data processing and analysis, and its potential to improve efficiency, safety, and decision-making.

Overall, edge computing has numerous applications in industrial automation, healthcare, and transportation, and can help improve efficiency, safety, and decision-making in these industries. By providing real-time processing and analysis of data, edge computing can help reduce latency and improve outcomes, and can also help improve security and privacy by reducing the amount of data that needs to be transmitted to the cloud or other remote locations. As the amount of data being generated continues to grow, edge computing is likely to play an increasingly important role in these industries, and is an area that is worth further research and exploration [46]. The future of edge computing in these industries will depend on its ability to address the challenges related to security, privacy, and scalability, and to provide more accurate and reliable data analysis [47].

## 4 Challenges and Open Research Issues in Edge Computing

### 4.1 Security and Privacy Challenges

Edge computing, despite its numerous benefits, including reduced latency and improved real-time processing, faces significant security and privacy challenges that can impact its performance, efficiency, and scalability. One of the primary concerns is the risk of data breaches, which can occur due to the decentralized nature of edge computing [5]. When data is processed and stored at the edge of the network, it becomes more vulnerable to unauthorized access, as the data is no longer confined to a centralized cloud or data center. This risk is exacerbated by the fact that edge devices often have limited security capabilities and may not be as well-maintained or updated as regularly as cloud-based infrastructure, highlighting the need for robust security measures to protect against such threats.

Another significant security challenge in edge computing is the threat of authentication attacks [48]. As edge devices and applications become more prevalent, the potential for unauthorized access and malicious activity increases. Authentication protocols must be robust and secure to prevent such attacks, which can compromise the integrity of the entire edge computing system. Furthermore, the use of IoT devices in edge computing introduces additional security risks, as these devices often have weak passwords and inadequate security measures, making them easy targets for hackers. These security risks can have a direct impact on the resource management and optimization strategies employed in edge computing, as discussed in the subsequent section.

Privacy is also a major concern in edge computing, particularly as it relates to the collection, processing, and storage of personal data. Edge computing applications, such as smart home devices and autonomous vehicles, often rely on the collection and analysis of sensitive personal data, which must be protected from unauthorized access and misuse. The use of machine learning models in edge computing also raises privacy concerns, as these models can potentially be used to infer sensitive information about individuals. Ensuring the privacy and security of personal data is essential to maintaining trust in edge computing applications and services.

In addition to these challenges, edge computing also faces issues related to secure data storage and transmission. As data is generated and processed at the edge, it must be stored and transmitted securely to prevent unauthorized access and eavesdropping. This requires the use of secure communication protocols and encryption methods, which can add complexity and overhead to edge computing systems. Developing efficient and effective security solutions is crucial to addressing these challenges and ensuring the widespread adoption of edge computing.

To address these security and privacy challenges, researchers and developers are exploring various solutions, including the use of blockchain technology [49]. These solutions aim to provide secure and private data processing and storage at the edge, while also ensuring the integrity and authenticity of the data. By leveraging these solutions and developing new security protocols, edge computing can provide a more secure and trustworthy environment for applications and services.

In conclusion, security and privacy are critical concerns in edge computing, and addressing these challenges is essential to ensuring the widespread adoption and success of edge computing applications. By understanding the security and privacy risks associated with edge computing and developing effective solutions to mitigate these risks, we can create a more secure and trustworthy edge computing ecosystem that can efficiently manage resources and optimize performance.

### 4.2 Resource Management and Optimization Challenges

Resource management and optimization are crucial challenges in edge computing, as they directly impact the performance, efficiency, and scalability of edge-based systems. Building on the security and privacy concerns discussed earlier, it is essential to address these challenges to ensure the widespread adoption and success of edge computing applications. One of the primary concerns is energy efficiency, as edge devices and servers are often resource-constrained and have limited power supply [50]. To address this, researchers have proposed various energy-aware resource allocation strategies, such as dynamic voltage and frequency scaling, and power-aware task scheduling [51]. These strategies aim to minimize energy consumption while meeting the required quality of service (QoS) and performance constraints, which is critical in maintaining the security and integrity of edge computing systems.

Another significant challenge is resource allocation, which involves assigning computing, storage, and communication resources to edge devices and applications [52]. Effective resource allocation is essential to ensure that edge devices can handle the increasing demand for compute-intensive and latency-sensitive applications, while also addressing the security and privacy concerns associated with data processing and storage. Researchers have explored various resource allocation techniques, including machine learning-based approaches, to optimize resource utilization and minimize waste [53]. By optimizing resource allocation, edge computing systems can reduce the risk of data breaches and unauthorized access, which is a critical security concern.

In addition to energy efficiency and resource allocation, edge computing also faces challenges related to task offloading, which involves deciding whether to execute tasks locally on edge devices or offload them to more powerful edge servers or cloud data centers [54]. Task offloading requires careful consideration of factors such as network latency, bandwidth, and server availability, as well as the trade-off between energy consumption and performance [55]. This challenge is closely related to the security and privacy concerns discussed earlier, as task offloading can introduce additional security risks if not properly managed.

To address these challenges, researchers have proposed various optimization frameworks and algorithms, such as linear programming, dynamic programming, and reinforcement learning [56]. These frameworks and algorithms aim to optimize resource allocation, task offloading, and energy efficiency in edge computing systems, while ensuring that QoS and performance constraints are met. Furthermore, edge computing also requires efficient management of multiple resources, including computing, storage, and communication resources [57]. This requires a comprehensive understanding of the complex interactions between these resources and the development of optimized resource management strategies. Researchers have explored various approaches, including resource virtualization, containerization, and orchestration, to manage multiple resources in edge computing systems [58].

In conclusion, resource management and optimization are critical challenges in edge computing, requiring careful consideration of energy efficiency, resource allocation, task offloading, and multiple resource management. By addressing these challenges, edge computing can provide a more efficient, scalable, and sustainable solution for supporting the growing demand for compute-intensive and latency-sensitive applications, while also ensuring the security and privacy of data processing and storage. As edge computing continues to evolve, ongoing research aims to develop more efficient and effective resource management strategies, which will be critical in enabling the widespread adoption of edge computing applications [59].

## 5 Conclusion and Future Directions

### 5.1 Conclusion and Summary of Findings

In conclusion, this survey provides a comprehensive overview of the current state of edge computing, its applications, and the challenges it faces. The emergence of edge computing has been driven by the need for low-latency processing, real-time decision-making, and reduced bandwidth usage [1]. As highlighted in [5], security and privacy are critical concerns in edge computing, and addressing these challenges is essential for the widespread adoption of edge computing. The various applications of edge computing, including IoT, smart cities, industrial automation, healthcare, transportation systems, and gaming, have the potential to revolutionize these industries by providing real-time processing, reduced latency, and improved security [60] [61].

The integration of artificial intelligence (AI) and machine learning (ML) in edge computing is a growing trend, with many applications leveraging these technologies to improve performance and efficiency [6]. The importance of edge AI in processing real-time data at the edge of the network, reducing latency, and improving decision-making is highlighted [62]. However, edge AI also faces challenges, including resource constraints, security threats, and scalability issues [63]. Furthermore, the survey discusses the importance of edge computing in enabling emerging technologies such as 5G and the Internet of Things (IoT) [46], and the need for sustainable edge computing, with a focus on energy efficiency, resource management, and environmental sustainability [64].

The survey highlights that edge computing faces several challenges, including security, privacy, resource management, and scalability, which must be addressed to realize its full potential [7]. Future research directions include exploring new architectures, technologies, and applications for edge computing, as well as addressing the challenges and limitations of current edge computing systems [65]. As edge computing continues to evolve, it is expected to play a critical role in supporting the low-latency, high-bandwidth requirements of emerging technologies, and its development will have a significant impact on society and industry, enabling new use cases and applications that can transform various sectors, as discussed in the subsequent section.

### 5.2 Future Directions and Recommendations

As edge computing continues to evolve, its integration with emerging technologies such as 5G, AI, and blockchain is expected to play a crucial role in enabling new use cases and applications. Building on the previous discussion of edge computing's current state and challenges, it is clear that the convergence of edge computing and 5G [66] will be essential in providing low-latency, high-bandwidth, and ultra-reliable communication services. This, in turn, will enable mission-critical applications such as autonomous vehicles, smart cities, and industrial automation, which were previously highlighted as key areas where edge computing can have a significant impact.

The integration of edge computing with AI [6] is also expected to enable real-time processing and analysis of data at the edge, leading to improved decision-making and automation. Furthermore, the use of blockchain technology [67] in edge computing is expected to provide a secure and decentralized platform for data management and processing, enabling secure and transparent data sharing, as well as improved data integrity and authenticity. The potential of edge computing to enable new applications and use cases is vast, and its integration with other emerging technologies such as augmented reality, virtual reality, and the Internet of Things (IoT) [3] will be critical in realizing this potential.

In terms of future research directions, several areas need to be explored to fully realize the potential of edge computing. The development of new edge computing architectures and frameworks that can support the integration of multiple emerging technologies [68] is essential. Additionally, the investigation of new use cases and applications that can be enabled by the integration of edge computing with emerging technologies [69] is necessary. The development of new security and privacy mechanisms that can protect data and ensure secure communication in edge computing environments [70] is also crucial.

The impact of edge computing on society and industry will be significant, with potential applications in industrial automation [71], smart cities [17], and healthcare [72]. As edge computing continues to evolve, it is expected to play a critical role in supporting the low-latency, high-bandwidth requirements of emerging technologies, and its development will have a profound impact on various sectors. The future of edge computing will be shaped by its integration with emerging technologies, and it is essential to continue exploring its potential and developing new solutions and mechanisms to support its growth and development [73]. Ultimately, the widespread adoption of edge computing will depend on addressing the challenges and limitations of current edge computing systems, and the development of new edge computing architectures, frameworks, and security mechanisms will be critical in realizing this goal.


## References

[1] Edge Computing: A Comprehensive Survey of Current Initiatives and a Roadmap for a Sustainable Edge Computing Development

[2] Internet of Things (IoT) and New Computing Paradigms

[3] Edge Computing for IoT

[4] Mobile Edge Computing

[5] Edge Security: Challenges and Issues

[6] Edge AI: A Taxonomy, Systematic Review and Future Directions

[7] Edge Computing: A Systematic Mapping Study

[8] A Survey on Dialogue Summarization: Recent Advances and New Frontiers

[9] Generating a Structured Summary of Numerous Academic Papers: Dataset and Method

[10] Controllable Text Summarization: Unraveling Challenges, Approaches, and Prospects -- A Survey

[11] Spot the BlindSpots: Systematic Identification and Quantification of Fine-Grained LLM Biases in Contact Center Summaries

[12] Layer 2 Blockchain Scaling: a Survey

[13] The State and Fate of Summarization Datasets: A Survey

[14] ShortScience.org - Reproducing Intuition

[15] Paving the way for mature secondary research: the seven types of literature review

[16] Euclidean lattices: theory and applications

[17] Edge Computing in IoT: A 6G Perspective

[18] Cloud, Fog, or Edge: Where to Compute?

[19] EdgeSphere: A Three-Tier Architecture for Cognitive Edge Computing

[20] Edge Computing Performance Amplification

[21] Edge-Cloud Collaborative Computing on Distributed Intelligence and Model Optimization: A Survey

[22] Fog Networking: An Overview on Research Opportunities

[23] All one needs to know about fog computing and related edge computing paradigms: A complete survey

[24] On Using Micro-Clouds to Deliver the Fog

[25] ECLM: Efficient Edge-Cloud Collaborative Learning with Continuous Environment Adaptation

[26] FedFog: Resource-Aware Federated Learning in Edge and Fog Networks

[27] HealthFog: An ensemble deep learning based Smart Healthcare System for Automatic Diagnosis of Heart Diseases in integrated IoT and fog computing environments

[28] Container Orchestration in Edge and Fog Computing Environments for Real-Time IoT Applications

[29] Application Component Placement in NFV-based Hybrid Cloud/Fog Systems

[30] Safe Testing

[31] Intelligent Energy Management with IoT Framework in Smart Cities Using Intelligent Analysis: An Application of Machine Learning Methods for Complex Networks and Systems

[32] Real-Time MDNet

[33] Fog Computing for Sustainable Smart Cities: A Survey

[34] Edge, Fog, and Cloud Computing : An Overview on Challenges and Applications

[35] Real-Time Agile Software Management for Edge and Fog Computing Based Smart City Infrastructure

[36] Software Defined Edge Computing for Distributed Management and Scalable Control in IoT Multinetworks

[37] Edge-Computing-Enabled Smart Cities: A Comprehensive Survey

[38] Enhancing Predictive Maintenance in Mining Mobile Machinery through a TinyML-enabled Hierarchical Inference Network

[39] Remote patient monitoring using artificial intelligence: Current state, applications, and challenges

[40] EdgeLaaS: Edge Learning as a Service for Knowledge-Centric Connected Healthcare

[41] Distributed Vehicular Computing at the Dawn of 5G: a Survey

[42] AI-Driven Vehicle Condition Monitoring with Cell-Aware Edge Service Migration

[43] Edge Computing for Smart Health: Context-Aware Approaches, Opportunities, and Challenges

[44] Real-Time Human Detection as an Edge Service Enabled by a Lightweight CNN

[45] Blockchain Powered Edge Intelligence for U-Healthcare in Privacy Critical and Time Sensitive Environment

[46] 6G White Paper on Edge Intelligence

[47] Analyzing Transformer Models and Knowledge Distillation Approaches for Image Captioning on Edge AI

[48] Cryptanalysis of authentication and key establishment protocol in Mobile Edge Computing Environment

[49] How BlockChain Can Help Enhance The Security And Privacy in Edge Computing?

[50] Energy-Efficient Task Offloading and Resource Allocation for Multiple Access Mobile Edge Computing

[51] Energy Minimization for Mobile Edge Computing Networks with Time-Sensitive Constraints

[52] Multiple Resource Allocation in Multi-Tenant Edge Computing via Sub-modular Optimization

[53] FELARE: Fair Scheduling of Machine Learning Tasks on Heterogeneous Edge Systems

[54] Joint Task Offloading and Resource Allocation for Multi-Server Mobile-Edge Computing Networks

[55] Energy-aware Resource Management for Federated Learning in Multi-access Edge Computing Systems

[56] Joint Optimization of Signal Design and Resource Allocation in Wireless D2D Edge Computing

[57] A Taxonomy for Management and Optimization of Multiple Resources in Edge Computing

[58] EdgeMORE: Improving Resource Allocation with Multiple Options from Tenants

[59] Sustainable Edge Computing: Challenges and Future Directions

[60] Edge Computing for IoT: Novel Insights from a Comparative Analysis of Access Control Models

[61] Edge Intelligence: Architectures, Challenges, and Applications

[62] Edge Intelligence: Paving the Last Mile of Artificial Intelligence with Edge Computing

[63] Deep Learning at the Edge

[64] Green Edge AI: A Contemporary Survey

[65] Roadmap for Edge AI: A Dagstuhl Perspective

[66] 5G: Agent for Further Digital Disruptive Transformations

[67] Blockchain for Mobile Edge Computing: Consensus Mechanisms and Scalability

[68] Edge Computing Architectures for Enabling the Realisation of the Next Generation Robotic Systems

[69] Mobile Edge Computing for the Metaverse

[70] Privacy Preserving Data Analytics in 5G-Enabled IoT for the Financial Industry

[71] Leveraging Machine Learning for Industrial Wireless Communications

[72] Edge AI for Internet of Energy: Challenges and Perspectives

[73] Towards Self-learning Edge Intelligence in 6G


