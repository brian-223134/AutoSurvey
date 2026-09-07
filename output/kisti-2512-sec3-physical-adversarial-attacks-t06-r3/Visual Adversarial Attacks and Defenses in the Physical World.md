# Visual Adversarial Attacks and Defenses in the Physical World

## 1 Introduction to Visual Adversarial Attacks

### 1.1 Concept and Impact of Visual Adversarial Attacks

Visual adversarial attacks refer to the process of crafting inputs to computer vision systems that are designed to cause the system to make a mistake. These attacks can be launched in both the digital and physical worlds, and they pose a significant threat to the security and reliability of computer vision systems. In the digital world, visual adversarial attacks typically involve adding small perturbations to an image that are imperceptible to the human eye, but that can cause a computer vision system to misclassify the image [1]. For example, an attacker might add a small amount of noise to an image of a stop sign that would cause a self-driving car's computer vision system to misclassify the sign as a yield sign. This type of attack highlights the vulnerability of computer vision systems to subtle manipulations, which can have serious consequences in real-world applications.

The physical world also presents opportunities for visual adversarial attacks, where an attacker can use various methods such as stickers, posters, or other objects to manipulate the input to a computer vision system [2]. For instance, an attacker might place a sticker on a stop sign that would cause a self-driving car's computer vision system to misclassify the sign as a yield sign. These types of attacks are particularly concerning because they can be used to cause physical harm or damage. The impact of such attacks can be significant, and it is essential to understand the mechanisms and consequences of visual adversarial attacks to develop effective countermeasures.

The consequences of visual adversarial attacks can be severe, especially in applications such as self-driving cars, surveillance systems, and medical diagnosis [3]. For example, if a self-driving car's computer vision system misclassifies a stop sign as a yield sign, the car may not stop at the sign, which could result in a serious accident. Similarly, if a surveillance system misclassifies an image of a person as an object, it may not be able to track the person's movement or detect suspicious activity. Furthermore, visual adversarial attacks can also be used to evade object detection systems, which are designed to detect and track objects in images or videos [4]. This can have serious implications for security and safety.

To address the vulnerability of computer vision systems to visual adversarial attacks, researchers are exploring various approaches to improve the robustness of these systems. One approach is to use adversarial training, which involves training a computer vision system on a dataset that includes images that have been perturbed to cause the system to make a mistake [5]. Another approach is to use input preprocessing techniques, such as data augmentation or normalization, to reduce the impact of visual adversarial attacks. Additionally, researchers are also exploring the use of more advanced techniques, such as meta-learning and transfer learning, to improve the robustness of computer vision systems to visual adversarial attacks [6]. By developing a deeper understanding of visual adversarial attacks and their consequences, we can work towards creating more robust and secure computer vision systems.

The development of effective defense mechanisms against visual adversarial attacks is crucial to ensure the security and reliability of computer vision systems. As these systems become increasingly ubiquitous in various applications, the risk of visual adversarial attacks also increases. Therefore, it is essential to continue researching and developing new techniques to counter these attacks and improve the robustness of computer vision systems [7]. By acknowledging the significance of visual adversarial attacks and their potential consequences, we can take the first step towards creating a more secure and reliable computer vision ecosystem. This will be further explored in the subsequent section, which delves into the categorization of visual adversarial attacks and their unique characteristics.

### 1.2 Types of Visual Adversarial Attacks

Visual adversarial attacks can be categorized into different types based on the level of manipulation and the goal of the attack. These types include pixel-level, object-level, and scene-level attacks, each with its unique characteristics and challenges. Understanding these categories is essential to developing effective defense mechanisms against visual adversarial attacks.

Pixel-level attacks involve manipulating the pixels of an image to cause a misclassification [8]. These attacks can be further divided into two subcategories: sparse attacks, which modify a small number of pixels, and dense attacks, which modify a large number of pixels. Sparse attacks are more challenging to detect, as they only modify a few pixels, while dense attacks are more noticeable but can be more effective [9]. Pixel-level attacks can be used to attack image classification models, object detection models, and semantic segmentation models, highlighting the need for robust defense mechanisms to prevent misclassifications.

Object-level attacks involve adding or modifying objects within an image to cause a misclassification [10]. These attacks can be used to attack object detection models and semantic segmentation models. Object-level attacks are more challenging to detect than pixel-level attacks, as they involve modifying the objects within an image rather than just the pixels. Object-level attacks can be used to add or remove objects from an image, or to modify the appearance of objects, making them a significant threat to the security of computer vision models.

Scene-level attacks involve manipulating the entire scene or environment to cause a misclassification [11]. These attacks can be used to attack object detection models, semantic segmentation models, and image classification models. Scene-level attacks are the most challenging to detect, as they involve modifying the entire scene rather than just a few pixels or objects. Scene-level attacks can be used to modify the lighting, weather, or other environmental factors within an image, making them a critical concern for computer vision models deployed in real-world applications.

In addition to these types of attacks, there are also other types of visual adversarial attacks, such as attacks on video object segmentation [12], 3D point clouds [13], and other computer vision tasks. These attacks involve manipulating the input data to cause a misclassification or to compromise the security of the model, emphasizing the need for comprehensive defense mechanisms to protect against various types of attacks.

The development of effective defense mechanisms against visual adversarial attacks requires a deep understanding of the types of attacks and their characteristics. This includes understanding the different types of attacks, such as pixel-level, object-level, and scene-level attacks, as well as the various techniques used to launch these attacks. It also requires an understanding of the computer vision models being attacked, including their strengths and weaknesses, and the types of data they are trained on. By acknowledging the significance of visual adversarial attacks and their potential consequences, we can take the first step towards creating a more secure and reliable computer vision ecosystem.

As the importance of defense mechanisms against visual adversarial attacks cannot be overstated, researchers have been actively exploring various approaches to improve the robustness of computer vision models. This includes the development of adversarial training methods, which involve training models on adversarial examples to improve their robustness. It also includes the development of input preprocessing techniques, such as data augmentation and normalization, which can help to reduce the effectiveness of adversarial attacks. Additionally, there are detection and certification methods, such as [14], which can be used to detect and certify the robustness of models against adversarial attacks.

In conclusion, visual adversarial attacks are a significant threat to the security and reliability of computer vision models, and understanding their types and characteristics is crucial to developing effective defense mechanisms. By recognizing the importance of defense mechanisms and the need for a comprehensive approach to address visual adversarial attacks, we can ensure the security and reliability of computer vision models and prevent the misuse of these models for malicious purposes, ultimately leading to a more secure and reliable computer vision ecosystem.

### 1.3 Importance of Defense Mechanisms

The importance of defense mechanisms against visual adversarial attacks cannot be overstated, as highlighted in the previous discussion on the various types of visual adversarial attacks and their potential consequences. As [7] notes, the vulnerability of deep learning models to adversarial attacks poses a significant threat to their deployment in safety-critical applications. The potential use of visual adversarial attacks in malicious activities, such as evading object detection or classification systems, further emphasizes the need for effective defense mechanisms. For instance, [15] demonstrates the feasibility of conducting real-time physical attacks on face recognition systems using adversarial light projections, underscoring the real-world implications of these attacks.

The real-world implications of visual adversarial attacks are far-reaching and can have severe consequences, particularly in applications such as autonomous vehicles. In this context, [16] shows that adversarial attacks can compromise the safety of passengers and pedestrians. Similarly, [17] demonstrates the vulnerability of multi-task visual perception models to adversarial attacks, which can have devastating consequences in safety-critical applications. Furthermore, [18] highlights the potential for natural phenomena, such as shadows, to be used as a means of launching physical-world adversarial attacks, emphasizing the need for comprehensive defense strategies.

To mitigate these risks, the development of effective defense mechanisms against visual adversarial attacks is crucial. As [5] notes, certified defenses can provide a robust guarantee against adversarial patches, which are a common type of visual adversarial attack. Moreover, [19] highlights the importance of considering the cost and utility of adversarial attacks when developing defense mechanisms, particularly in scenarios where the attacker has limited resources or capabilities. In addition to certified defenses, other approaches have been proposed to defend against visual adversarial attacks, including attention mechanisms and logit regularization methods. For example, [20] proposes a novel attack method that leverages attention mechanisms to boost the transferability of facial adversarial examples, while [21] demonstrates the effectiveness of logit regularization methods in improving the robustness of deep learning models against adversarial attacks.

The importance of defense mechanisms against visual adversarial attacks is also highlighted by the potential for these attacks to be used in conjunction with other types of attacks. For instance, [22] demonstrates the potential for cross-modal obfuscation attacks to be used in conjunction with visual adversarial attacks to bypass safety mechanisms in large vision-language models. Similarly, [23] highlights the potential for multi-faceted attacks to be used to expose cross-model vulnerabilities in defense-equipped vision-language models, emphasizing the need for a comprehensive approach to defense. As [24] notes, ensuring the safety of multimodal large language models without compromising their performance is a crucial challenge that requires a multifaceted approach, taking into account the complex and evolving nature of the threat landscape. Ultimately, the development of effective defense mechanisms against visual adversarial attacks is essential to preventing the misuse of these models for malicious purposes and ensuring their safe and reliable deployment in real-world applications.

## 2 Background on Adversarial Attacks

### 2.1 Introduction to Adversarial Attacks

Adversarial attacks have become a significant concern in the field of machine learning and deep learning, as they can compromise the security and reliability of AI systems. In this subsection, we introduce the basic concept of adversarial attacks, including their definition, types, and goals, to provide a foundation for understanding the threat models and attack goals discussed in the subsequent section. Adversarial attacks refer to the process of crafting input data that can mislead a machine learning model into producing incorrect or undesired outputs [25]. These attacks can be launched in various forms, including images, audio, and text, and can be used to compromise the security of AI systems in different applications, such as image classification, speech recognition, and natural language processing [26].

One of the key characteristics of adversarial attacks is that they are designed to be imperceptible to humans, meaning that the input data is modified in a way that is not noticeable to the human eye or ear [27]. For example, an adversarial attack on an image classification system might involve adding a small amount of noise to an image that is not noticeable to humans, but can cause the system to misclassify the image. Similarly, an adversarial attack on a speech recognition system might involve adding a small amount of background noise that is not noticeable to humans, but can cause the system to misrecognize the spoken words [28]. This imperceptibility highlights the need for a thorough understanding of adversarial attacks and their potential impact on AI systems.

Adversarial attacks can be categorized into different types based on their goals and characteristics. One common categorization is into white-box and black-box attacks [29]. White-box attacks assume that the attacker has full access to the machine learning model, including its architecture, parameters, and training data. Black-box attacks, on the other hand, assume that the attacker has no knowledge of the model's internal workings and can only observe the input and output of the system [30]. Another categorization is into targeted and non-targeted attacks [30]. Targeted attacks aim to mislead the system into producing a specific output, while non-targeted attacks aim to cause the system to produce any incorrect output [31]. Understanding these different types of attacks is crucial for developing effective defense mechanisms.

The goals of adversarial attacks can vary depending on the context and the motivations of the attacker. In some cases, the goal may be to compromise the security of an AI system, such as by causing a self-driving car to misrecognize a stop sign [32]. In other cases, the goal may be to compromise the privacy of individuals, such as by causing a speech recognition system to reveal sensitive information [28]. Adversarial attacks can also be used to compromise the reliability of AI systems, such as by causing a image classification system to produce incorrect or misleading results [31]. These varying goals underscore the importance of considering the potential threat models and attack goals, as discussed in the subsequent section.

The concept of adversarial attacks has been studied extensively in the field of machine learning and deep learning, and various methods have been proposed to defend against these attacks [33]. One common approach is to use adversarial training, which involves training the model on a dataset that includes adversarial examples [34]. Another approach is to use input preprocessing techniques, such as data augmentation and normalization, to reduce the effectiveness of adversarial attacks [35]. Additionally, various detection and certification methods have been proposed to identify and certify the robustness of machine learning models against adversarial attacks [36]. These defense mechanisms will be further discussed in the context of threat models and attack goals in the subsequent section.

In conclusion, adversarial attacks are a significant concern in the field of machine learning and deep learning, and can compromise the security, reliability, and privacy of AI systems. Understanding the concept of adversarial attacks, including their definition, types, and goals, is essential for developing effective defense mechanisms against these attacks [37]. Furthermore, the development of effective defense mechanisms against adversarial attacks requires a deep understanding of the goals and motivations of the attackers, as well as the limitations and vulnerabilities of AI systems [38]. This understanding will be crucial in addressing the threat models and attack goals discussed in the subsequent section, and in ensuring the security and reliability of AI systems in the physical world.

### 2.2 Threat Models and Attack Goals

Threat models and attack goals are crucial components of adversarial attacks, as they define the objectives and strategies of the attackers. As discussed in the previous section, adversarial attacks can compromise the security, reliability, and privacy of AI systems, and understanding the threat models and attack goals is essential for developing effective defense mechanisms. In the context of adversarial attacks, threat models refer to the hypothetical scenarios that describe the potential attacks on a system, while attack goals represent the desired outcomes of these attacks. Various threat models and attack goals have been identified in the literature, including integrity, availability, and confidentiality attacks, which can have severe consequences, including financial losses, reputational damage, and even physical harm [39].

Integrity attacks aim to compromise the accuracy and reliability of a system's data or outputs, which can be achieved by manipulating the training data of a machine learning model to produce incorrect or misleading results [39]. For instance, an attacker may attempt to compromise the integrity of a system's software or hardware components to disrupt its normal functioning [40]. Integrity attacks can have significant consequences, including financial losses, reputational damage, and even physical harm. To mitigate these threats, it is essential to develop and implement effective defense strategies and countermeasures, such as data validation and verification, to ensure the accuracy and reliability of a system's data or outputs.

Availability attacks, on the other hand, focus on disrupting the accessibility or usability of a system or its resources, which can be launched through various means, such as denial-of-service (DoS) or distributed denial-of-service (DDoS) attacks, malware or ransomware attacks [41]. These attacks can overwhelm a system with traffic, making it unavailable to legitimate users, or encrypt or delete sensitive data, making it inaccessible to authorized users [42]. The consequences of availability attacks can be significant, including loss of productivity, revenue, and customer trust. To prevent these attacks, organizations should prioritize security awareness and training, as well as incident response planning, to ensure that they are prepared to respond to and manage adversarial attacks [43].

Confidentiality attacks aim to compromise the secrecy or privacy of a system's data or communications, which can involve unauthorized access, interception, or theft of sensitive information, such as personal data, financial information, or intellectual property [44]. These attacks can be launched through various means, including phishing, social engineering, or exploitation of software vulnerabilities [45]. The consequences of confidentiality attacks can be severe, including identity theft, financial fraud, and reputational damage. To mitigate these threats, organizations should implement effective defense strategies and countermeasures, such as encryption, access control, and intrusion detection, to protect their systems and data from unauthorized access or interception.

In addition to these traditional threat models, new attack goals and strategies have emerged in the context of adversarial attacks, such as compromising the explainability or transparency of a system, making it difficult to understand or trust its decisions or outputs [46]. Others may aim to compromise the fairness or accountability of a system, leading to biased or discriminatory outcomes [47]. To address these emerging threats, organizations should stay informed about new attack goals and strategies, as well as emerging defense techniques and countermeasures [48]. By prioritizing security awareness, training, and incident response planning, organizations can reduce the risk of adversarial attacks and ensure the confidentiality, integrity, and availability of their systems and data.

In conclusion, threat models and attack goals play a critical role in understanding and mitigating adversarial attacks, and recognizing the various types of threat models and attack goals, including integrity, availability, and confidentiality attacks, is essential for developing effective defense strategies and countermeasures. As the threat landscape continues to evolve, it is crucial to stay informed about new attack goals and strategies, as well as emerging defense techniques and countermeasures, to ensure the security and reliability of AI systems in the physical world [49]. The next section will discuss the various defense strategies and countermeasures that can be used to mitigate the effects of adversarial attacks, including the development of more advanced methods, such as anomaly detection and machine learning-based defenses.

### 2.3 Adversarial Attack Techniques and Methodologies

Adversarial attacks on machine learning models have become a significant concern in recent years, with various techniques and methodologies being developed to generate adversarial examples. As discussed in the previous section, threat models and attack goals play a critical role in understanding and mitigating adversarial attacks. In the context of visual adversarial attacks, the attack techniques and methodologies can be categorized into several types, including gradient-based attacks, score-based attacks, and decision-based attacks.

Gradient-based attacks are one of the most common types of adversarial attacks, which utilize the gradient of the loss function to generate adversarial examples. These attacks typically involve computing the gradient of the loss function with respect to the input, and then using this gradient to update the input in a direction that maximizes the loss [50]. For example, the Fast Gradient Sign Method (FGSM) [51] is a popular gradient-based attack that uses the sign of the gradient to update the input. Another example is the Projected Gradient Descent (PGD) attack [52], which uses a more sophisticated optimization algorithm to generate adversarial examples.

In addition to gradient-based attacks, score-based attacks utilize the output scores of the model to generate adversarial examples. These attacks typically involve computing the score of the model for a given input, and then using this score to update the input in a direction that maximizes the score [53]. For example, the Carlini and Wagner (CW) attack [51] is a popular score-based attack that uses the output score of the model to generate adversarial examples. Decision-based attacks, on the other hand, utilize the output decision of the model to generate adversarial examples, and typically involve computing the decision of the model for a given input, and then using this decision to update the input in a direction that maximizes the loss [53].

The development of these attack techniques and methodologies has also led to the creation of more advanced attacks, such as transfer attacks, ensemble attacks, reinforcement learning-based attacks, and evolutionary algorithm-based attacks. For example, the Transfer Attack [54] is a type of attack that utilizes a surrogate model to generate adversarial examples that can be transferred to the target model. Another example is the Ensemble Attack [55], which utilizes an ensemble of models to generate adversarial examples that can be used to attack the target model. Recent studies have also explored the use of reinforcement learning to generate adversarial examples [56], and evolutionary algorithms to generate adversarial examples [57].

Understanding these different types of attacks is crucial for developing effective defenses against adversarial examples [58]. In the next section, we will discuss the various defense strategies and countermeasures that can be used to mitigate the effects of adversarial attacks in the physical world. By recognizing the types of attacks and their corresponding countermeasures, organizations can develop a comprehensive approach to protecting their systems and data from adversarial attacks.

## 3 Types of Visual Adversarial Attacks

### 3.1 Pixel-Level Attacks

Pixel-level attacks are a fundamental type of visual adversarial attack where the adversary manipulates the pixels of an image to cause a misclassification. This type of attack is particularly concerning because it can be used to compromise the security of computer vision systems, such as self-driving cars, surveillance systems, and facial recognition systems. In a pixel-level attack, the adversary adds noise to the input image, which can be imperceptible to the human eye, but can cause the computer vision system to misclassify the image [59]. The subtlety of these attacks makes them especially challenging to detect and defend against, highlighting the need for robust defense mechanisms.

One of the key challenges in defending against pixel-level attacks is their ability to be very subtle and difficult to detect. For example, an attacker can add noise to a small number of pixels in an image, which can cause the computer vision system to misclassify the image, but may not be noticeable to the human eye [8]. This subtlety underscores the importance of developing effective detection and defense strategies that can identify such minute alterations. Furthermore, the effectiveness of pixel-level attacks in causing misclassifications, even with minimal modifications, underscores their potential to have serious consequences in real-world applications, such as causing a self-driving car to misclassify a stop sign as a speed limit sign [60].

There are several types of pixel-level attacks, including one-pixel attacks, where the attacker modifies a single pixel in the image to cause a misclassification [61], and multi-pixel attacks, where the attacker modifies multiple pixels in the image to cause a misclassification [62]. These variations in attack strategies necessitate a comprehensive approach to defense, one that can adapt to the diverse methods an attacker might employ. To defend against pixel-level attacks, several techniques have been proposed, including adversarial training, where the computer vision system is trained on a dataset that includes adversarial examples [63], and input preprocessing, such as image denoising or compression, to remove the noise added by the attacker [64].

In addition to these techniques, several papers have proposed using pixel-level analysis to detect and defend against pixel-level attacks. For example, [65] proposes using a pixel-level analysis to detect and defend against pixel-level attacks. This approach involves analyzing the pixels in the image to detect any anomalies or noise that may indicate a pixel-level attack. Such analytical methods can provide valuable insights into the nature of pixel-level attacks and how they can be effectively countered.

Overall, pixel-level attacks pose a significant threat to the security and reliability of computer vision systems due to their subtlety and potential for causing serious misclassifications. The development of effective defense mechanisms against these attacks is crucial and requires a multifaceted approach that includes adversarial training, input preprocessing, and pixel-level analysis. As research in this area continues to evolve, it is essential to consider the dynamic nature of these threats and the need for adaptive defense strategies [66]. Furthermore, exploring the vulnerabilities that pixel-level attacks exploit can also shed light on how to improve the robustness and security of computer vision models against a broader range of adversarial threats [67].

### 3.2 Object-Level Attacks

Object-level attacks are a type of visual adversarial attack where the adversary adds or modifies objects within an image to cause a misclassification. This type of attack is particularly challenging to defend against, as it can be difficult to distinguish between legitimate and malicious objects in an image. In [68], the authors propose a targeted feature space attack method that can mislead detectors to fabricate extra designated objects, regardless of whether the victim image contains objects or not. 

Building on the concept of pixel-level attacks, which manipulate the pixels of an image to cause a misclassification, object-level attacks take a more nuanced approach by targeting specific objects within an image. Object-level attacks can be further categorized into two sub-types: object insertion and object modification. Object insertion attacks involve adding a new object to an image, while object modification attacks involve modifying an existing object in the image. In [69], the authors propose a novel generative attack that leverages local patch differences in multi-object scenes to optimize the perturbation generator. 

Another example of object-level attacks is the [70] attack, which leverages contextual information inherent in semantic segmentation models to enhance backdoor performance. This attack highlights the importance of considering the context in which an object is being attacked, a concept that will be further explored in the subsequent discussion of scene-level attacks. 

Object-level attacks can also be used to attack vision-language models, such as those used in image captioning tasks. In [71], the authors propose an object-oriented method to craft poisons, which aims to modify pixel values by a slight range with the modification number proportional to the scale of the current detected object region. 

In addition to these examples, object-level attacks have been proposed in various other contexts, including [72], [73], and [74]. 

To defend against object-level attacks, various defense mechanisms have been proposed, including [64] and [75]. These defense mechanisms are crucial in preventing object-level attacks from compromising the security of computer vision models. 

In conclusion, object-level attacks are a powerful and versatile type of visual adversarial attack that can be used to fool object detectors and other computer vision models. These attacks can be used to insert or modify objects in an image, and have been shown to be highly effective in various scenarios and applications. As we transition to discussing scene-level attacks, it is essential to recognize the connection between object-level and scene-level attacks, as both types of attacks can be used to manipulate the context in which an image is being classified. By understanding the nuances of object-level attacks, we can better appreciate the challenges and implications of scene-level attacks, which will be explored in the subsequent subsection. 

Moreover, object-level attacks can be used in physical attacks, such as [76]. 

In [77], the authors propose a proactive framework that leverages structured disentanglement to identify and neutralize both seen and unseen backdoor threats at the dataset level. 

Overall, object-level attacks are a significant threat to computer vision security, and further research is needed to develop effective defense mechanisms and to improve our understanding of these attacks and their implications. By exploring the various types of object-level attacks and their applications, we can better understand the vulnerabilities of computer vision models and develop more effective defense strategies to mitigate these threats.

### 3.3 Scene-Level Attacks

Scene-level attacks are a type of visual adversarial attack where the adversary manipulates the entire scene or environment to cause a misclassification. This type of attack is particularly challenging to defend against, as it can be difficult to distinguish between legitimate and malicious changes to the scene. In this subsection, we will explore the concept of scene-level attacks and discuss some of the key techniques and strategies used to launch these attacks.

One of the key challenges in defending against scene-level attacks is that they can be highly context-dependent. For example, an attack that involves adding a small object to a scene may be effective in one context but not in another. This means that defenders need to be able to understand the context in which the attack is being launched and to develop strategies that can adapt to different scenarios. [70] has shown that contextual information can be used to enhance the effectiveness of backdoor attacks, highlighting the importance of considering context when developing defenses.

Another challenge in defending against scene-level attacks is that they can be highly subtle. For example, an attack that involves changing the lighting or texture of a scene may be difficult to detect, especially if the changes are small. [78] has demonstrated that even small changes to the input data can have a significant impact on the performance of a deep neural network, highlighting the need for defenders to be able to detect and respond to subtle changes.

Scene-level attacks can also be highly flexible, allowing attackers to adapt to different scenarios and to evade detection. For example, an attack that involves adding a small object to a scene can be modified to add different objects or to change the location of the object. [79] has shown that backdoor attacks can be designed to be highly flexible, allowing attackers to specify arbitrary target classes and to adapt to different scenarios.

In addition to their flexibility, scene-level attacks can also be highly effective. For example, an attack that involves changing the lighting or texture of a scene can be highly effective in causing a misclassification, especially if the changes are subtle. [80] has demonstrated that texture-based attacks can be highly effective in causing misclassifications, highlighting the need for defenders to be able to detect and respond to changes in the texture of a scene.

To defend against scene-level attacks, defenders need to be able to develop strategies that can adapt to different scenarios and that can detect and respond to subtle changes. One approach is to use techniques such as data augmentation, which involves generating multiple versions of a scene and using them to train a deep neural network. [81] has shown that data augmentation can be effective in defending against backdoor attacks, highlighting the potential of this approach for defending against scene-level attacks.

Another approach is to use techniques such as adversarial training, which involves training a deep neural network on a dataset that includes adversarial examples. [82] has demonstrated that adversarial training can be effective in defending against evasion attacks, highlighting the potential of this approach for defending against scene-level attacks.

In conclusion, scene-level attacks are a highly challenging type of visual adversarial attack that can be difficult to defend against. They can be highly context-dependent, subtle, flexible, and effective, making them a significant threat to deep neural networks. To defend against these attacks, defenders need to be able to develop strategies that can adapt to different scenarios and that can detect and respond to subtle changes. Techniques such as data augmentation and adversarial training show promise for defending against scene-level attacks, but further research is needed to develop effective defenses against these attacks. [67] has shown that backdoor attacks can be highly effective in causing misclassifications, highlighting the need for defenders to be able to detect and respond to these attacks.

The development of scene-level attacks has significant implications for the development of deep neural networks. For example, it highlights the need for defenders to be able to consider the context in which an attack is being launched and to develop strategies that can adapt to different scenarios. It also highlights the need for defenders to be able to detect and respond to subtle changes, such as changes in the lighting or texture of a scene. [83] has demonstrated that latent space poisoning can be used to generate out-of-distribution adversarial examples, highlighting the need for defenders to be able to detect and respond to these types of attacks.

As we move forward to discuss other types of visual adversarial attacks, it is essential to consider the challenges and implications of scene-level attacks. The next subsection will explore other types of visual adversarial attacks, including attacks on video object segmentation, 3D point clouds, and other computer vision tasks, and discuss how these attacks can be used to compromise the security of deep neural networks. [84] has demonstrated that local intrinsic dimensionality can be used to characterize adversarial subspaces, highlighting the potential of this approach for defending against scene-level attacks and other types of visual adversarial attacks. [85] has shown that black-box adversarial attacks can be highly effective in causing misclassifications, highlighting the need for defenders to be able to detect and respond to these types of attacks.

### 3.4 Other Types of Visual Adversarial Attacks

Other types of visual adversarial attacks have also been explored in recent years, including attacks on video object segmentation, 3D point clouds, and other computer vision tasks. For instance, [12] demonstrates the vulnerability of video object segmentation models to adversarial attacks, which can lead to significant errors in segmentation results. Similarly, [86] provides a comprehensive overview of adversarial attacks and defenses on 3D point cloud classification, highlighting the importance of considering the robustness of 3D point cloud models to adversarial attacks. These attacks can be seen as an extension of scene-level attacks, which can be highly context-dependent, subtle, flexible, and effective, as discussed in the previous subsection.

The vulnerability of 3D point cloud models to adversarial attacks is further highlighted by [87], which proposes a method to generate minimal adversarial examples for 3D point cloud classification. This work shows that even small perturbations to the point cloud can lead to misclassification, emphasizing the need for robust defense mechanisms. Furthermore, [88] introduces a surface-based adversarial attack on 3D point clouds, which can be used to attack facial expression recognition models, demonstrating the potential of these attacks to compromise various computer vision tasks.

In addition to these areas, other computer vision tasks such as semantic segmentation, object detection, and image classification have also been shown to be vulnerable to adversarial attacks. For example, [27] demonstrates the vulnerability of semantic segmentation and object detection models to adversarial attacks, which can lead to significant errors in detection and segmentation results. Similarly, [89] shows that camera-based 3D object detection models can be vulnerable to adversarial attacks, which can lead to significant errors in detection results. These findings emphasize the importance of developing robust defense mechanisms that can adapt to various scenarios and computer vision tasks.

Moreover, [13] proposes a method to attack 3D local feature extractors using adversarial patches, which can lead to significant errors in feature extraction results. This work highlights the importance of considering the robustness of 3D local feature extractors to adversarial attacks. Furthermore, [90] evaluates the robustness of 3D point cloud completion models to adversarial attacks, which can lead to significant errors in completion results. These studies demonstrate the need for a comprehensive approach to defending against visual adversarial attacks, one that considers the unique challenges and vulnerabilities of various computer vision tasks.

Other types of visual adversarial attacks include attacks on deep learning-based image segmentation models, such as [91], which demonstrates the vulnerability of deep learning-based image segmentation models to adversarial attacks. Similarly, [92] proposes a method to prevent adversarial attacks on semantic segmentation models using denoising autoencoders. These approaches highlight the potential of developing task-specific defense mechanisms that can improve the robustness of computer vision models to adversarial attacks.

In addition, [93] proposes a method to attack segment anything models using adversarial examples, which can lead to significant errors in segmentation results. Furthermore, [94] proposes a method to improve the robustness of object detection models to adversarial attacks, which can lead to significant improvements in detection results. These studies demonstrate the ongoing efforts to develop more robust computer vision models and defense mechanisms, highlighting the importance of continued research in this area.

Finally, [95] provides a comprehensive overview of adversarial attacks in object detection, highlighting the importance of considering the robustness of object detection models to adversarial attacks. This work demonstrates the vulnerability of object detection models to adversarial attacks and highlights the need for developing more robust models that can withstand such attacks. As we move forward to discuss defense mechanisms against visual adversarial attacks, it is essential to consider the various types of attacks and their unique challenges, as well as the ongoing efforts to develop more robust computer vision models and defense mechanisms.

## 4 Defense Mechanisms Against Visual Adversarial Attacks

### 4.1 Adversarial Training Methods

Adversarial training methods have been widely recognized as one of the most effective defense mechanisms against visual adversarial attacks. The core idea behind adversarial training is to augment the training dataset with adversarial examples, which are generated by adding perturbations to the original input images. By training the model on these adversarial examples, it can learn to be more robust and resilient to attacks. In this subsection, we will discuss various adversarial training methods, including adversarial training with different types of attacks, and explore how these methods can be used to improve the robustness of models against visual adversarial attacks.

One of the most common adversarial training methods is the Fast Gradient Sign Method (FGSM) [96]. FGSM is a simple and efficient method for generating adversarial examples, which involves adding a perturbation to the input image in the direction of the gradient of the loss function. This method has been shown to be effective in improving the robustness of models against adversarial attacks. However, it has also been shown that FGSM-based adversarial training can be vulnerable to stronger attacks, such as the Projected Gradient Descent (PGD) attack [97]. To address this limitation, several variants of FGSM have been proposed, including the Iterative FGSM (I-FGSM) method [98] and the Momentum Iterative FGSM (MI-FGSM) method [30].

In addition to FGSM-based methods, other adversarial training methods have been proposed, including the PGD attack [97] and the Carlini and Wagner (C&W) attack [99]. These methods involve generating adversarial examples using different optimization algorithms, which can lead to more effective attacks. Adversarial training with different types of attacks has also been explored, such as multi-strength adversarial training [100], which involves generating adversarial examples using different types of attacks, including FGSM, PGD, and C&W. This approach has been shown to be effective in improving the robustness of models against multiple types of attacks.

Furthermore, adversarial training has been combined with other defense mechanisms, such as input preprocessing techniques and detection-based methods [101]. For example, [102] proposes a masked weight adversarial training method, which involves adding adversarial perturbations to the weights of the model during training. This approach has been shown to be effective in improving the generalization of models, while also improving their robustness against adversarial attacks. Additionally, transferable adversarial examples [103] can be used to improve the robustness of models against adversarial attacks, while also reducing the computational cost of adversarial training.

In conclusion, adversarial training methods have been widely recognized as one of the most effective defense mechanisms against visual adversarial attacks. By leveraging various adversarial training methods, including FGSM-based methods, PGD-based methods, and C&W-based methods, and combining them with other defense mechanisms, such as input preprocessing techniques and detection-based methods, it is possible to further improve the robustness of models against adversarial attacks. As we will discuss in the next subsection, input preprocessing techniques are also essential in defending against visual adversarial attacks, and can be used in conjunction with adversarial training methods to improve the overall robustness of models [104]. Future research directions include exploring new adversarial training methods, improving the efficiency of adversarial training, and developing more effective defense mechanisms against visual adversarial attacks [97].

### 4.2 Input Preprocessing Techniques

Input preprocessing techniques are a crucial component of defense mechanisms against visual adversarial attacks, as they can be used to transform the input data in a way that makes it more difficult for attackers to craft successful attacks. Building on the concept of adversarial training discussed in the previous subsection, input preprocessing techniques can be used in conjunction with adversarial training methods to further improve the robustness of models against visual adversarial attacks. In this subsection, we will discuss various input preprocessing techniques, including data augmentation, normalization, and feature extraction, and explore how these techniques can be used to defend against visual adversarial attacks.

Data augmentation is a technique that involves generating new training data by applying transformations to the existing data, such as rotation, scaling, and flipping. By increasing the size and diversity of the training data, data augmentation can help to improve the robustness of models against visual adversarial attacks [105]. For example, [106] proposes a framework for learning compositional augmentation policies for text classification. This technique can be particularly effective when used in conjunction with adversarial training methods, such as FGSM and PGD, to further improve the robustness of models.

Normalization is another important input preprocessing technique, which involves scaling the input data to a common range, usually between 0 and 1. This can help to improve the stability and robustness of models against visual adversarial attacks [104]. For example, [107] proposes an adaptive normalization technique that combines percentile-based ROI cropping with histogram standardization. Normalization can also be used to reduce the impact of adversarial perturbations, making it more difficult for attackers to craft successful attacks.

Feature extraction is also a crucial input preprocessing technique, which involves selecting the most relevant features from the input data and discarding the rest. This can help to reduce the dimensionality of the data and improve the robustness of models against visual adversarial attacks [108]. For example, [109] proposes a sparse compressed agglomeration technique for feature extraction and dimensionality reduction. By selecting the most relevant features, feature extraction can help to improve the accuracy and robustness of models, making them more resistant to visual adversarial attacks.

In addition to these techniques, there are other input preprocessing techniques that can be used to defend against visual adversarial attacks. For example, [110] proposes a colorful cutout technique that enhances image data augmentation with curriculum learning. Another technique is [111], which uses preprocessing techniques such as normalization, feature extraction, and classification to improve the accuracy of Arabic handwriting recognition. Furthermore, [112] proposes a learning-based assistant for data preprocessing that can help to improve the accuracy and robustness of models against visual adversarial attacks.

Moreover, [113] proposes an advanced image preprocessing technique that combines context-aware spatial decomposition with histogram standardization to improve the accuracy and robustness of breast cancer segmentation models. These techniques can be used in conjunction with detection and certification methods, which will be discussed in the following subsection, to provide a comprehensive defense mechanism against visual adversarial attacks.

In conclusion, input preprocessing techniques are essential in defending against visual adversarial attacks, and can be used in conjunction with adversarial training methods and detection and certification methods to provide a comprehensive defense mechanism. Techniques such as data augmentation, normalization, and feature extraction can be used to transform the input data in a way that makes it more difficult for attackers to craft successful attacks. By using these techniques, models can be made more robust against visual adversarial attacks, improving their accuracy and reliability in real-world applications. As shown in [114], the choice of preprocessing technique can significantly impact the performance of models against attacks, highlighting the importance of carefully selecting and evaluating preprocessing techniques for specific applications.

### 4.3 Detection and Certification Methods

Detection and certification methods are crucial components of defense mechanisms against visual adversarial attacks, building on the input preprocessing techniques and robust optimization methods discussed earlier. These methods aim to identify and certify the robustness of computer vision systems against various types of attacks, providing an additional layer of security. In this subsection, we will explore various detection and certification methods, including statistical methods, machine learning-based approaches, and certification techniques, and discuss how they can be used in conjunction with input preprocessing and robust optimization techniques.

Statistical methods are widely used for detecting anomalies in data and can be applied to detect visual adversarial attacks. These methods rely on statistical models to identify patterns and outliers in the data. For example, the Isolation Forest algorithm [115] is a statistical method that can be used to detect anomalies in network traffic data. This algorithm works by isolating the anomalies in the data, rather than profiling the normal data. Similarly, the Local Outlier Factor (LOF) algorithm [116] is another statistical method that can be used to detect anomalies in data. This algorithm works by calculating the local density of the data points and identifying the points that have a low density as anomalies.

Machine learning-based approaches are also widely used for detecting visual adversarial attacks and can be combined with statistical methods for improved detection. These approaches rely on machine learning models to learn the patterns and anomalies in the data. For example, the Random Forest algorithm [117] is a machine learning-based approach that can be used to detect financial fraud transactions. This algorithm works by training a random forest model on a dataset of legitimate and fraudulent transactions and using the model to predict the likelihood of a new transaction being fraudulent. Similarly, the Support Vector Machine (SVM) algorithm [118] is another machine learning-based approach that can be used to detect credit card fraud transactions. This algorithm works by training an SVM model on a dataset of legitimate and fraudulent transactions and using the model to predict the likelihood of a new transaction being fraudulent.

Certification techniques are also important for ensuring the robustness of computer vision systems against visual adversarial attacks and can be used in conjunction with detection methods. These techniques provide a formal guarantee that a system is robust against a certain type of attack. For example, the certification technique proposed in [119] provides a formal guarantee that a segmentation model is robust against adversarial attacks. This technique works by training a model to predict the segmentation mask of an image and then using a randomized smoothing algorithm to certify the robustness of the model.

In addition to these methods, there are also other approaches that can be used to detect and certify visual adversarial attacks, such as ensemble methods and federated learning approaches. For example, the ensemble method proposed in [120] can be used to detect fraud in imbalanced datasets. This method works by training an ensemble of models on a dataset of legitimate and fraudulent transactions and using the ensemble to predict the likelihood of a new transaction being fraudulent. Similarly, the federated learning approach proposed in [121] can be used to detect anomalies in federated learning settings. This approach works by training a model on a dataset of normal and anomalous data and using the model to predict the likelihood of a new data point being anomalous.

In conclusion, detection and certification methods are crucial components of defense mechanisms against visual adversarial attacks, complementing input preprocessing and robust optimization techniques. These methods can be used to identify and certify the robustness of computer vision systems against various types of attacks, providing an additional layer of security. Statistical methods, machine learning-based approaches, and certification techniques are some of the methods that can be used to detect and certify visual adversarial attacks. These methods have been widely used in various applications, including financial fraud detection, network anomaly detection, and image segmentation. By using these methods, we can ensure the robustness of computer vision systems against visual adversarial attacks and prevent the misuse of these systems for malicious purposes. [122], [123], [124], and [125] are some of the studies that have used these methods to detect and certify visual adversarial attacks.

### 4.4 Robust Optimization Techniques

Robust optimization techniques have gained significant attention in recent years due to their ability to improve the robustness of machine learning models against adversarial attacks. As discussed in the previous subsection, detection and certification methods are crucial components of defense mechanisms against visual adversarial attacks. However, these methods can be further enhanced by using robust optimization techniques, which can be broadly categorized into three main types: robust loss functions, regularization techniques, and optimization algorithms. 

Robust loss functions are designed to reduce the impact of outliers and noisy data on the model's performance. One such example is the Huber loss function, which is a combination of the mean squared error and the mean absolute error [126]. This loss function is more robust to outliers than the traditional mean squared error loss function. Another example is the Wasserstein loss function, which is based on the Wasserstein distance between two probability distributions [127]. This loss function is more robust to adversarial attacks than traditional loss functions.

Regularization techniques are used to reduce overfitting and improve the generalization of machine learning models. One such example is the L1 regularization technique, which adds a penalty term to the loss function to discourage large weights [128]. Another example is the L2 regularization technique, which adds a penalty term to the loss function to discourage large weights [129]. These regularization techniques can be used to improve the robustness of machine learning models against adversarial attacks.

Optimization algorithms are used to minimize the loss function and improve the performance of machine learning models. One such example is the stochastic gradient descent (SGD) algorithm, which is a popular optimization algorithm used in many machine learning models [130]. Another example is the Adam optimization algorithm, which is a variant of the SGD algorithm that adapts the learning rate for each parameter [131]. These optimization algorithms can be used to improve the robustness of machine learning models against adversarial attacks.

In addition to these techniques, there are several other robust optimization techniques that can be used to defend against visual adversarial attacks. One such example is the distributionally robust optimization (DRO) technique, which is a framework for optimizing the worst-case performance of a model over a set of possible distributions [132]. Another example is the robust principal component analysis (RPCA) technique, which is a method for separating a low-rank matrix from a sparse matrix [133]. These techniques can be used to improve the robustness of machine learning models against adversarial attacks.

The application of robust optimization techniques in defending against visual adversarial attacks has been explored in several studies. For example, [134] proposed a robust linear classification algorithm that uses a combination of robust loss functions and regularization techniques to improve the robustness of linear classification models. [135] proposed a fast image recovery algorithm that uses a combination of robust loss functions and optimization algorithms to improve the robustness of image recovery models.

In conclusion, robust optimization techniques are a powerful tool for defending against visual adversarial attacks. These techniques can be used to improve the robustness of machine learning models by reducing the impact of outliers and noisy data, reducing overfitting, and improving the generalization of models. The application of robust optimization techniques in defending against visual adversarial attacks has been explored in several studies, and these techniques have been shown to be effective in improving the robustness of machine learning models. As we move forward to the next subsection, we will explore other defense mechanisms against visual adversarial attacks, including input preprocessing techniques and ensemble methods.

Furthermore, [136] proposed a novel regularization approach as an alternative to adversarial training, which can improve the robustness of deep neural networks against adversarial examples. [137] discussed the interactions between regularization and interior point approaches and proposed an algorithm that synergistically combines them. [138] proposed a continuation algorithm that is applicable to a large class of nonsmooth regularized risk minimization problems and can be flexibly used with a number of existing solvers for the underlying smoothed subproblem.

In addition, [131] introduced a novel algorithmic framework that blends a general-purpose constrained-optimization solver with Constraint Folding, which can add more reliability and generality to the state-of-the-art robustness evaluation packages. [139] proposed a novel learning-based optimizer, called LRCO, which quickly outputs a robust solution in the presence of uncertain context. [140] provided a comprehensive overview of optimization techniques employed in training machine learning models, including gradient descent variants, adaptive learning rate methods, second-order optimization methods, regularization methods, constraint-based methods, and Bayesian optimization.

Overall, robust optimization techniques are a crucial component of defending against visual adversarial attacks, and their application has been explored in several studies. These techniques can be used to improve the robustness of machine learning models, and their development is an active area of research. Future research directions include exploring the application of robust optimization techniques in other domains and developing new robust optimization techniques that can be used to defend against visual adversarial attacks.

## 5 Physical World Considerations for Visual Adversarial Attacks

### 5.1 Environmental Factors Affecting Attack Effectiveness

Environmental factors play a crucial role in determining the effectiveness of visual adversarial attacks in the physical world, building upon the understanding of sensor limitations discussed earlier. Various factors such as lighting, weather, and viewpoint can significantly impact the success of an attack. For instance, [141] demonstrates that the performance of adversarial patches can be affected by factors such as patch size, position, rotation, brightness, and hue. The study reveals that the effectiveness of the attack can be reduced by up to 64% due to discrepancies in patch performance between the digital and physical worlds.

The presence of noise or interference in the physical world is another critical environmental factor that can affect the success of visual adversarial attacks. [142] highlights the challenges of launching physical adversarial attacks in the presence of real-world noise and interference. Furthermore, the viewpoint and orientation of the attacker or the target object can also impact the effectiveness of the attack, as investigated in [143], which demonstrates that the attack success rate can be significantly reduced when the viewpoint is changed.

Additionally, weather conditions such as fog, snow, or rain can significantly affect the effectiveness of visual adversarial attacks. [144] studies the impact of natural perturbations such as fog and snow on the robustness of deep learning models and demonstrates that these perturbations can significantly degrade the performance of the models. Similarly, [145] evaluates the robustness of semantic segmentation models against real-world adversarial patch attacks and demonstrates that the attack success rate can be reduced by up to 50% in the presence of weather conditions such as fog or rain.

Other environmental factors, such as the type of surface or material that the adversarial patch is applied to, can also impact the effectiveness of the attack. [146] demonstrates that the performance of adversarial patches can be affected by the surface roughness and texture of the target object. Moreover, the distance between the attacker and the target object can also impact the effectiveness of the attack, as studied in [147], which demonstrates that the attack success rate can be reduced by up to 50% when the distance between the attacker and the target object is increased.

The type of lighting used in the physical world is another crucial factor that can impact the effectiveness of visual adversarial attacks. [2] proposes the use of invisible light pulses to conduct adversarial attacks on deep neural networks and demonstrates that the attack success rate can be increased by up to 20% when the lighting conditions are optimized. Understanding these environmental factors is essential for designing and evaluating effective visual adversarial attacks, as well as developing robust defense strategies, which will be discussed in the subsequent section on sensor limitations and defense strategies. [18] highlights the importance of considering these factors when designing and evaluating visual adversarial attacks.

### 5.2 Sensor Limitations and Their Impact on Attack Effectiveness

Sensor limitations play a crucial role in determining the effectiveness of visual adversarial attacks in the physical world, as they can significantly impact the quality of the input data used by computer vision systems. Various sensors used in these systems, such as cameras, LIDAR, and radar, have their own set of limitations that can be exploited by attackers to increase the effectiveness of their attacks. For instance, cameras are susceptible to variations in lighting conditions, which can affect the quality of the captured image and subsequently impact the effectiveness of the attack [142]. Similarly, LIDAR sensors are limited by their resolution and range, which can make it difficult to detect and respond to adversarial attacks [148].

Understanding these sensor limitations is essential for designing and evaluating effective visual adversarial attacks, as well as developing robust defense strategies. The limitations of sensors can be exploited by attackers to increase the effectiveness of their attacks, such as using the knowledge of a camera's limited dynamic range to create an adversarial patch that is more likely to be detected by the camera [141]. Additionally, the fusion of multiple sensors can also impact the effectiveness of adversarial attacks, as it can introduce new vulnerabilities that can be exploited by attackers [149]. For example, an attacker can create an adversarial patch that is designed to exploit the differences in the way that different sensors perceive the environment [150].

The impact of sensor limitations on the effectiveness of adversarial attacks can also be influenced by the specific application and environment in which the attack is being carried out. For instance, in a low-light environment, an attacker may need to use a more powerful adversarial patch to ensure that it is detected by the camera [2]. Similarly, in a cluttered environment, an attacker may need to use a more sophisticated attack strategy to ensure that the adversarial object is not missed by the sensor [151]. These considerations highlight the need for robust and adaptive defense strategies that can account for the various sensor limitations and environmental factors that can impact the effectiveness of visual adversarial attacks.

To mitigate the impact of sensor limitations on the effectiveness of adversarial attacks, researchers have proposed a number of defense strategies. These strategies include improving the robustness of sensors to variations in lighting conditions and other environmental factors [152], using sensor fusion to combine the data from multiple sensors and improve the accuracy and robustness of the system [153], and developing more sophisticated attack detection algorithms that can detect and respond to adversarial attacks in real-time [154]. By addressing the limitations of sensors and developing more effective defense strategies, we can improve the security and robustness of computer vision systems and reduce the risk of adversarial attacks [155]. This is particularly important in real-world scenarios, where visual adversarial attacks can have significant consequences, and will be further discussed in the subsequent sections.

### 5.3 Real-World Deployment of Visual Adversarial Attacks

The deployment of visual adversarial attacks in real-world scenarios poses significant challenges and considerations, building upon the understanding of sensor limitations and their impact on the effectiveness of these attacks, as discussed earlier. One of the primary concerns is the ability of these attacks to withstand various environmental conditions, such as changes in lighting, weather, or viewpoint [145]. For instance, an adversarial patch designed to mislead a self-driving car's object detection system may not be effective in low-light conditions or when viewed from a different angle, highlighting the need for robustness in adversarial attacks. To address this issue, researchers have proposed methods to improve the robustness of adversarial attacks, such as using 3D modeling to simulate real-world environments [156].

Another challenge in deploying visual adversarial attacks is ensuring their stealthiness and inconspicuousness, which is crucial in avoiding detection by security systems or human observers [18]. Adversarial patches that are too conspicuous or attention-grabbing may be easily detected and mitigated, emphasizing the need for subtle and natural-looking attacks. To overcome this challenge, researchers have explored techniques to create more subtle and natural-looking adversarial patches, such as using natural phenomena like shadows or reflections to disguise the attack [18].

The scalability of visual adversarial attacks is also a significant consideration in real-world deployment, as the number of potential targets and environments increases, the complexity of designing and deploying effective adversarial attacks grows exponentially [141]. To address this challenge, researchers have proposed methods to improve the transferability of adversarial attacks across different models and environments, such as using meta-learning or multi-task learning approaches [157]. Furthermore, the development of standardized evaluation metrics and benchmarking frameworks is crucial to assess the effectiveness of different attack strategies and identify areas for improvement.

In addition to these technical challenges, the deployment of visual adversarial attacks in real-world scenarios also raises significant ethical and societal concerns, which must be carefully considered to ensure the safe and secure deployment of computer vision systems [17]. For instance, the use of adversarial attacks to manipulate self-driving cars or other autonomous systems could have devastating consequences, including loss of life or property damage. Similarly, the use of adversarial attacks to manipulate medical imaging systems or other healthcare technologies could have serious implications for patient safety and well-being [158]. To mitigate these risks, researchers and practitioners must prioritize the development of robust and effective defenses against visual adversarial attacks, including the use of techniques like adversarial training, input preprocessing, and detection-based methods to identify and mitigate potential attacks [159].

Ultimately, the real-world deployment of visual adversarial attacks highlights the need for increased awareness and education among stakeholders, including researchers, practitioners, and policymakers, to develop more effective defenses and mitigate the potential consequences of these attacks [15]. By understanding the potential risks and challenges associated with visual adversarial attacks, we can work to develop more effective defenses and ensure the safe and secure deployment of computer vision systems in a wide range of applications, which will be further discussed in the subsequent sections [160].

## 6 Evaluation Metrics and Benchmarking for Visual Adversarial Attacks

### 6.1 Introduction to Evaluation Metrics

Evaluation metrics play a crucial role in assessing the robustness of models against visual adversarial attacks, serving as a standardized way to measure the performance of models in the face of adversarial examples. The importance of these metrics cannot be overstated, as they enable the comparison of the effectiveness of different defense mechanisms and attack strategies, which is essential for advancing the field of visual adversarial attacks and defenses [95]. 

One of the primary challenges in evaluating the robustness of models against visual adversarial attacks is the lack of a unified evaluation framework [161]. This limitation can lead to conflicting results when using different evaluation metrics, making it essential to carefully select the metrics used to assess model robustness. For instance, metrics such as the $L_0$ and $L_\infty$ norms are commonly used to evaluate the robustness of models against adversarial attacks [161]. However, these metrics may not provide a comprehensive picture of model robustness, as they only consider the magnitude of the perturbation and not its impact on the model's performance.

To address this limitation, researchers have proposed alternative evaluation metrics that take into account the model's performance under different types of attacks [162]. For example, metrics such as the adversarial loss and the robust accuracy have been proposed to evaluate the robustness of models against adversarial attacks [163]. These metrics provide a more comprehensive picture of model robustness, as they consider both the magnitude of the perturbation and its impact on the model's performance. Furthermore, the design of the evaluation framework is also crucial in assessing the robustness of models against visual adversarial attacks [164]. The evaluation framework should be designed to test the model's robustness against a wide range of attacks, including white-box and black-box attacks [165].

The importance of evaluation metrics in assessing the robustness of models against visual adversarial attacks is further highlighted by the fact that different models may exhibit different levels of robustness against different types of attacks [166]. For instance, a model may be robust against $L_0$ attacks but vulnerable to $L_\infty$ attacks [161]. Therefore, it is essential to use a comprehensive set of evaluation metrics to assess the robustness of models against different types of attacks. By doing so, researchers can gain a deeper understanding of the strengths and weaknesses of different models and develop more effective defense mechanisms. 

In conclusion, evaluation metrics play a vital role in assessing the robustness of models against visual adversarial attacks. The choice of evaluation metrics and the design of the evaluation framework are crucial in providing a comprehensive picture of model robustness. By using a unified evaluation framework and a comprehensive set of evaluation metrics, researchers can compare the effectiveness of different defense mechanisms and attack strategies, ultimately advancing the field of visual adversarial attacks and defenses [95]. This will pave the way for the development of more robust models that can withstand various types of attacks, which is essential for ensuring the reliability and security of models in the physical world.

### 6.2 Taxonomy of Evaluation Metrics

The evaluation of visual adversarial attacks is a crucial aspect of understanding the robustness of models in the physical world, building upon the importance of evaluation metrics discussed in the previous section. As evaluation metrics play a vital role in assessing the robustness of models against visual adversarial attacks, various metrics have been proposed to assess the effectiveness of these attacks. A taxonomy of these metrics is essential to comprehend the strengths and weaknesses of each, and to develop more effective methods for evaluating the robustness of models.

One of the primary metrics used to evaluate the robustness of models is the attack success rate [95]. This metric measures the percentage of successful attacks, where success is defined as the model misclassifying the adversarial example. Another metric is the average perturbation distance, which measures the average distance between the original image and the adversarial example [167]. This metric provides insight into the amount of perturbation required to fool the model, and is closely related to the $L_0$ and $L_\infty$ norms discussed in the previous section.

In addition to these metrics, researchers have also proposed metrics that evaluate the robustness of models based on the type of attack. For example, the robustness metric proposed in [168] evaluates the robustness of models based on both $L_0$ and $L_\infty$ attacks. This metric provides a more comprehensive understanding of the model's robustness, as it takes into account both the number of pixels changed and the magnitude of the changes. Other metrics, such as the universal perturbation metric [169], evaluate the robustness of models based on the ability of a single perturbation to fool multiple models.

The retention score metric [170] evaluates the robustness of models based on their ability to retain their performance under adversarial attacks. This metric provides a more nuanced understanding of the model's robustness, as it takes into account the model's performance on both clean and adversarial examples. Furthermore, metrics such as the physical adversarial attack metric [142] evaluate the robustness of models based on their ability to withstand physical attacks, such as printing and re-scanning images.

The evaluation metrics can be categorized into two main categories: metrics that evaluate the robustness of models based on the attack's success rate, and metrics that evaluate the robustness of models based on the attack's characteristics, such as the amount of perturbation required to fool the model. The first category includes metrics such as the attack success rate [95], while the second category includes metrics such as the average perturbation distance [167]. These categories will be essential in the development of benchmarking frameworks, which will be discussed in the following section.

In conclusion, the taxonomy of evaluation metrics for visual adversarial attacks is diverse and complex. Different metrics provide insight into different aspects of the model's robustness, and a comprehensive understanding of these metrics is essential to evaluating the robustness of models in the physical world. By categorizing and describing these metrics, researchers can better understand the strengths and weaknesses of each metric and develop more effective methods for evaluating the robustness of models [164]. The development of new metrics, such as the retention score metric [170], provides a more nuanced understanding of the model's robustness and can help to identify potential vulnerabilities in the model. Overall, the evaluation of visual adversarial attacks is a critical aspect of ensuring the robustness of models in the physical world, and a thorough understanding of the taxonomy of evaluation metrics is essential to achieving this goal [7].

### 6.3 Benchmarking Frameworks

Benchmarking frameworks are essential for evaluating and comparing the effectiveness of different defense mechanisms and attack strategies against visual adversarial attacks, building upon the evaluation metrics discussed in the previous section. These frameworks provide a standardized platform for assessing the robustness of models and the potency of attacks, enabling researchers to identify the most effective approaches and areas for improvement. Several benchmarking frameworks have been established to address the challenges posed by visual adversarial attacks, including [171], [172], and [173].

One of the key features of these benchmarking frameworks is their ability to evaluate the performance of models against a wide range of attacks, which is crucial for understanding the robustness of models in the physical world. For instance, [171] provides a comprehensive evaluation of gradient-based attacks, including PGD, FGSM, and CW attacks. Similarly, [173] offers a platform for evaluating the robustness of models against multiple attacks, including Lp-based threat models, spatial transformations, and color changes. These frameworks enable researchers to assess the effectiveness of different defense mechanisms, such as adversarial training, input preprocessing, and detection methods, against various types of attacks.

The benchmarking frameworks also facilitate the comparison of different attack strategies, which is essential for developing effective defense mechanisms. [172] provides a comprehensive evaluation of backdoor attacks, including poison-based, label-based, and trigger-based attacks. This framework enables researchers to compare the effectiveness of different backdoor attacks and defense mechanisms, providing valuable insights into the strengths and weaknesses of various approaches. Similarly, [174] offers a platform for evaluating the safety of large language models against jailbreaking attacks, including prompt injection, context manipulation, and instruction override attacks.

In addition to evaluating the performance of models and attacks, benchmarking frameworks also provide a platform for identifying research gaps and areas for improvement. [175] highlights the need for more robust defense mechanisms against federated learning attacks, including backdoor attacks and data poisoning attacks. Similarly, [176] emphasizes the importance of developing more effective defense mechanisms against vertical federated learning attacks, including data inference attacks and model inversion attacks.

The development of benchmarking frameworks has also led to the creation of new evaluation metrics and methodologies, which will be further discussed in the following sections. [177] introduces a new benchmark framework for evaluating the transferability of adversarial attacks, including generative structure, semantic similarity, gradient editing, target modification, and ensemble approach. This framework provides a comprehensive evaluation of the transferability of adversarial attacks, enabling researchers to assess the effectiveness of different defense mechanisms against transferable attacks.

Furthermore, benchmarking frameworks have facilitated the development of more robust and generalizable defense mechanisms. [178] proposes a heterogeneous model combinatorial defense framework for defending against adversarial attacks, including a combination of different models, such as CNNs, RNNs, and transformers. This framework provides a more robust and generalizable defense mechanism against various types of attacks, including Lp-based threat models, spatial transformations, and color changes.

In conclusion, benchmarking frameworks play a vital role in evaluating and comparing the effectiveness of different defense mechanisms and attack strategies against visual adversarial attacks. These frameworks provide a standardized platform for assessing the robustness of models and the potency of attacks, enabling researchers to identify the most effective approaches and areas for improvement. The development of benchmarking frameworks has led to the creation of new evaluation metrics and methodologies, facilitating the development of more robust and generalizable defense mechanisms. As the field of visual adversarial attacks continues to evolve, the importance of benchmarking frameworks will only continue to grow, providing a foundation for the development of more effective and robust defense mechanisms [179], [180], and [181].

## 7 Real-World Applications and Case Studies

### 7.1 Autonomous Vehicle Systems

Autonomous vehicle systems have become a crucial area of research in the field of computer vision, with a focus on developing robust and secure systems that can withstand various types of attacks. Visual adversarial attacks, in particular, have gained significant attention in recent years due to their potential to compromise the safety and security of autonomous vehicles. As a natural extension of the vulnerabilities observed in surveillance systems, autonomous vehicle systems are also susceptible to visual adversarial attacks, which can have devastating consequences. In this subsection, we will provide real-world examples and case studies of visual adversarial attacks and defenses in autonomous vehicle systems, highlighting the need for robust defense mechanisms to ensure public safety and security.

One of the most significant concerns in autonomous vehicle systems is the vulnerability of their perception modules to adversarial attacks. These modules, which are responsible for detecting and recognizing objects in the environment, can be deceived by carefully crafted adversarial examples. For instance, [182] demonstrates the possibility of creating physical adversarial examples that can deceive traffic sign recognition systems in autonomous vehicles. The authors propose a novel attack pipeline that generates adversarial samples which are robust to environmental conditions and noisy image transformations present in the physical world. Similarly, [183] proposes a method for generating physical-world-resilient adversarial examples that can mislead autonomous driving systems in a continuous manner.

The vulnerability of autonomous vehicle systems to visual adversarial attacks is further exacerbated by the complexity of their perception modules. For example, [17] presents a detailed analysis of adversarial attacks on multi-task visual perception in autonomous driving. The authors demonstrate that their attacks can successfully deceive the perception system of an autonomous vehicle, highlighting the need for more robust defense mechanisms. Moreover, [184] presents a method for generating simple physical adversarial examples that can deceive end-to-end autonomous driving models, underscoring the importance of developing effective defense strategies.

To defend against these types of attacks, researchers have proposed various defense mechanisms, including adversarial training, input preprocessing, and detection and certification methods. For example, [185] proposes a novel adversarial training method that combines vulnerability-aware and curiosity-driven approaches to enhance the robustness of autonomous vehicle systems. Similarly, [186] presents a framework for generating physical adversarial patches that can be used to evaluate the security of object detection systems in autonomous vehicles. These defense mechanisms are crucial in preventing attacks such as [187], which can hijack the visual perception system of an autonomous vehicle, causing it to make incorrect decisions.

In terms of real-world applications, visual adversarial attacks and defenses in autonomous vehicle systems have significant implications for safety and security. For instance, [188] demonstrates the possibility of creating physical adversarial examples that can deceive automated lane centering systems in autonomous vehicles. To mitigate these types of attacks, it is essential to develop more robust defense mechanisms that can detect and respond to visual adversarial attacks in real-time. For example, [189] proposes a dynamic ensemble approach that can detect and respond to adversarial attacks in real-time, using a combination of consistency checks and data fusion techniques. Similarly, [190] presents a moving target defense approach that can be used to protect embedded deep visual sensing systems against adversarial examples.

In conclusion, visual adversarial attacks and defenses in autonomous vehicle systems are a significant concern for safety and security. The examples and case studies presented in this subsection demonstrate the vulnerability of autonomous vehicle systems to various types of visual adversarial attacks and highlight the need for more robust defense mechanisms. As the field of autonomous vehicles continues to evolve, it is essential to prioritize the development of robust and secure systems that can withstand various types of attacks, including visual adversarial attacks. This is particularly important in the context of surveillance systems, where visual adversarial attacks can have significant consequences for public safety and security, as discussed in the following subsection. [191] and [192] are some of the papers that have addressed the issue of security in autonomous vehicles and have proposed novel methods to improve the robustness of these systems.

### 7.2 Surveillance Systems

Surveillance systems are a critical component of modern security infrastructure, and their vulnerability to visual adversarial attacks poses a significant threat to public safety and security. [193] highlights the risks associated with adversarial attacks on surveillance systems, where an adversary can physically change their appearance to avoid detection, tracking, and recognition. This vulnerability is particularly concerning, as surveillance systems are often used in conjunction with autonomous vehicle systems, which are also susceptible to visual adversarial attacks, as discussed in the previous subsection.

One notable example of a visual adversarial attack on a surveillance system is the use of adversarial t-shirts or glasses to evade face recognition systems. [194] demonstrates the effectiveness of such attacks, where a real-time system employing the ShuffleNet V1 transfer-learning algorithm was trained on a Kaggle dataset for face mask detection accuracy. Similarly, [182] proposes a novel attack that exploits the concept of adversarial examples to modify innocuous signs and advertisements in the environment, causing a state-of-the-art ImageNet deep learning model to misclassify them with high confidence.

In addition to these examples, [18] introduces a new type of optical adversarial examples that use natural phenomena, such as shadows, to achieve stealthy and effective physical-world adversarial attacks. These attacks can be particularly challenging to detect, as they can be designed to evade digital signal processing-based detection methods. To defend against such attacks, [195] proposes a novel method for detecting and segmenting adversarial graphics patterns from images.

Furthermore, [196] introduces a new detection method for UAV vision systems that uses attribution maps created by model visualization techniques. This approach can be used to detect and analyze the physical characteristics of an individual's appearance, such as the shape and texture of their face, to determine whether they are genuine or not. In terms of defense mechanisms, [5] proposes a certified defense against patch attacks, which is the first of its kind. Additionally, [197] evaluates the effectiveness of preprocessing defenses against adversarial attacks on reidentification systems.

The vulnerability of surveillance systems to visual adversarial attacks has significant implications for public safety and security. As face recognition systems become increasingly prevalent in various aspects of our lives, the need for effective defense mechanisms against visual adversarial attacks will become even more pressing. In the following subsection, we will discuss the vulnerability of face recognition systems to visual adversarial attacks and the various defense mechanisms that have been proposed to mitigate these attacks. [15] provides a comprehensive survey of physical adversarial attacks on camera-based smart systems, including surveillance systems. [7] provides a comprehensive review of adversarial attacks in computer vision, including their challenges and defense strategies.

In conclusion, surveillance systems are vulnerable to visual adversarial attacks, which can compromise their effectiveness and pose a significant threat to public safety and security. Developing effective defense mechanisms against such attacks is crucial to ensuring the security and reliability of surveillance systems. [95] provides a comprehensive survey and evaluation of adversarial attacks in object detection, including their challenges and defense strategies. The development of robust defense mechanisms against visual adversarial attacks will require a multidisciplinary approach, involving researchers from a range of fields, including computer vision, machine learning, and security. [198] proposes a novel approach to craft and camouflage physical-world adversarial examples into natural styles that appear legitimate to human observers.

### 7.3 Face Recognition Systems

Face recognition systems have become increasingly prevalent in various aspects of our lives, from security and surveillance to social media and personal devices. However, these systems are not without their vulnerabilities, particularly when it comes to visual adversarial attacks [199]. These attacks can take many forms, including digital and physical attacks, and can be used to evade detection, impersonate individuals, or disrupt the functioning of the system [200]. As discussed in the previous section, surveillance systems are also vulnerable to visual adversarial attacks, which can compromise their effectiveness and pose a significant threat to public safety and security.

One of the key challenges in defending against visual adversarial attacks on face recognition systems is the need for robust and effective detection methods. Traditional defense methods often rely on digital signal processing techniques, such as noise reduction and filtering, to detect and remove adversarial perturbations [201]. However, these methods can be limited in their effectiveness, particularly against more sophisticated attacks. To address this challenge, researchers have proposed a range of new detection methods, including those based on deep learning [202] and computer vision [203]. These methods can be used to detect and analyze the physical characteristics of an individual's face, such as the shape and texture of the face, to determine whether the face is genuine or not.

In addition to detection methods, researchers have also explored the use of adversarial training as a means of defending against visual adversarial attacks on face recognition systems [204]. Adversarial training involves training the face recognition system on a dataset that includes adversarial examples, with the goal of improving the system's robustness to these types of attacks. This approach has been shown to be effective in improving the security of face recognition systems, particularly when combined with other defense methods [205]. Furthermore, the use of generative adversarial networks (GANs) has been proposed as a means of defending against visual adversarial attacks on face recognition systems [206]. GANs can be used to generate synthetic faces that can be used to train face recognition systems, improving their robustness to adversarial attacks.

Despite the progress that has been made in defending against visual adversarial attacks on face recognition systems, there are still many challenges that remain to be addressed. One of the key challenges is the need for more effective and robust detection methods, particularly against physical attacks [207]. Physical attacks, such as those that use printed masks or other physical objects to disguise an individual's face, can be particularly challenging to detect, as they can be designed to evade digital signal processing-based detection methods [208]. To address the challenge of physical attacks, researchers have proposed a range of new detection methods, including those based on computer vision and machine learning [209]. These methods can be used to detect and analyze the physical characteristics of an individual's face, such as the shape and texture of the face, to determine whether the face is genuine or not.

In conclusion, visual adversarial attacks on face recognition systems are a significant challenge that must be addressed in order to ensure the security and accuracy of these systems. Researchers have proposed a range of new detection methods and defense strategies, including adversarial training, computer vision-based detection, and liveness detection, to defend against these types of attacks. However, there are still many challenges that remain to be addressed, particularly in the area of physical attacks. Further research is needed to develop more effective and robust detection methods, as well as to improve the overall security and accuracy of face recognition systems [210]. The development of face recognition systems that are robust to visual adversarial attacks will require a multidisciplinary approach, involving researchers from a range of fields, including computer vision, machine learning, and security. As the field continues to evolve, it is likely that face recognition systems will become even more prevalent, and the need for effective and robust defense methods against visual adversarial attacks will become even more pressing, leading to new applications and domains where these attacks can be applied, such as medical image analysis and vision-language models, which will be discussed in the following section.

### 7.4 Other Applications

Visual adversarial attacks and defenses have been explored in various applications beyond autonomous vehicles, surveillance systems, and face recognition systems, which were discussed in the previous section. For instance, in the realm of medical image analysis, [158] highlights the vulnerability of deep learning models to adversarial attacks, which can have severe consequences in healthcare. Similarly, [211] investigates the factors affecting the adversarial attack vulnerability of medical image analysis systems, emphasizing the need for robust defenses in this domain.

In addition to medical image analysis, visual adversarial attacks and defenses have been applied to object detection, where [11] proposes a method to generate universal physical camouflage attacks that can effectively attack object detectors in the wild. This work demonstrates the potential risks of adversarial attacks in real-world applications, such as self-driving cars or surveillance systems. Furthermore, [145] evaluates the robustness of semantic segmentation models against real-world adversarial patch attacks, highlighting the importance of developing robust defenses for computer vision systems.

The application of visual adversarial attacks and defenses in the realm of vision-language models is also an area of growing interest. [212] proposes a novel attack framework that exploits the multi-modal nature of vision-language models, demonstrating the vulnerability of these models to adversarial attacks. In contrast, [159] presents a defense mechanism that leverages text-to-image models to detect adversarial samples in vision-language models, showcasing the potential for developing effective defenses against such attacks.

Moreover, visual adversarial attacks and defenses have been explored in the context of recommender systems, where [213] proposes a framework for securing visually-aware recommender systems against adversarial attacks, which can have significant implications for applications such as e-commerce or social media. The emergence of new technologies, such as 3D modeling and augmented reality, has also created new avenues for visual adversarial attacks and defenses. [156] proposes a method for generating adversarial patches using 3D modeling, demonstrating the potential for creating more sophisticated and realistic attacks. In contrast, [214] presents a method for generating adversarial camouflages that can suppress both model and human attention, highlighting the need for developing effective defenses against such attacks.

In conclusion, visual adversarial attacks and defenses have been explored in a wide range of applications, from medical image analysis and object detection to vision-language models and recommender systems. The growing interest in this area has led to the development of new attack and defense methods, which have significant implications for the security and robustness of computer vision systems. As the field continues to evolve, it is essential to develop effective defenses against visual adversarial attacks and to explore new applications and domains where these attacks can be applied, which will be further discussed in the following sections. [7] provides a comprehensive overview of the challenges and defense strategies in computer vision, highlighting the need for continued research in this area. [142] presents a decade-long survey of physical adversarial attacks in computer vision, demonstrating the growth and evolution of this field over the years.

## 8 Challenges, Future Directions, and Conclusion

### 8.1 Challenges and Open Problems

Despite the significant progress made in the field of visual adversarial attacks and defenses, there are still several challenges and open problems that need to be addressed. One of the major challenges is the lack of a comprehensive understanding of the underlying mechanisms of visual adversarial attacks [17]. Most existing defense mechanisms are designed to mitigate specific types of attacks, but they often fail to generalize to other types of attacks or scenarios. This highlights the need for more robust and generalizable defense mechanisms that can effectively counter a wide range of visual adversarial attacks. Furthermore, the development of such mechanisms requires a deeper understanding of the complex interplay between adversarial attacks and the underlying visual models.

Another challenge is the trade-off between robustness and accuracy [21]. Many defense mechanisms that are designed to improve robustness often come at the cost of reduced accuracy on clean data. This trade-off is particularly problematic in applications where high accuracy is critical, such as in autonomous driving or medical imaging. Therefore, there is a need to develop defense mechanisms that can balance robustness and accuracy, and provide a good trade-off between these two competing objectives. To achieve this, researchers must investigate new approaches that can optimize both robustness and accuracy, such as the use of adversarial training or input preprocessing techniques.

In addition to these challenges, the development of more effective attack methods is also an open problem [215]. While there have been significant advances in the development of attack methods, such as the use of adversarial patches [11] and targeted attacks [212], there is still a need for more sophisticated and effective attack methods that can be used to evaluate the robustness of visual models. The evaluation of visual adversarial attacks and defenses is also a challenging task [216]. Most existing evaluation metrics are based on simple metrics such as accuracy or robustness, but these metrics often fail to capture the complexity of visual adversarial attacks.

The development of more robust and generalizable visual models is also a key open problem [217]. One of the key challenges is the development of models that can effectively generalize to new and unseen data, while also being robust to visual adversarial attacks. This requires the development of models that can learn to recognize and respond to a wide range of visual patterns and anomalies, while also being able to adapt to new and changing environments. Moreover, the development of more effective defense mechanisms against physical-world attacks is crucial [142]. Physical-world attacks are a significant threat to the robustness and reliability of visual models, as they can be used to manipulate and deceive models in a wide range of applications.

To address these challenges, it is essential to develop a better understanding of the underlying mechanisms of visual perception and cognition [218]. Visual perception and cognition are complex and multi-faceted processes that involve the integration of multiple sources of information, including visual, auditory, and tactile cues. Therefore, there is a need to develop models that can effectively capture and represent these complex processes, while also being robust to visual adversarial attacks. Ultimately, the development of more comprehensive and nuanced frameworks for understanding and evaluating the robustness and accuracy of visual models is necessary [219]. By developing such frameworks, researchers and practitioners can gain a better understanding of the challenges and open problems in the field of visual adversarial attacks and defenses, and develop more effective and robust visual models that can be used in a wide range of applications, paving the way for future research directions in this field [3].

### 8.2 Future Research Directions

Future research directions in the field of visual adversarial attacks and defenses are vast and varied, with many potential avenues for exploration. As the field continues to evolve, it is essential to identify areas that require further investigation to improve the security and robustness of computer vision systems. One promising area of research is the development of novel attack strategies that can effectively evade detection by current defense mechanisms [171]. For example, researchers could investigate the use of generative models to create more sophisticated and realistic adversarial examples [220]. This could help to uncover vulnerabilities in current defense mechanisms and inform the development of more robust systems.

Another important direction for future research is the establishment of standardized benchmarks and evaluation criteria for visual adversarial attacks and defenses [221]. This would enable researchers to compare the effectiveness of different defense mechanisms and attack strategies in a fair and consistent manner, facilitating the development of more robust and reliable systems [222]. The creation of open-source toolkits and frameworks, such as BackFed, could provide a common platform for researchers to develop and test new attack and defense strategies [223]. By establishing standardized benchmarks and evaluation criteria, researchers can ensure that their work is building on a solid foundation and that the field is progressing in a cohesive and meaningful way.

The emergence of large language models (LLMs) and other advanced AI technologies also presents new opportunities and challenges for visual adversarial attacks and defenses [224]. For instance, researchers could investigate the use of LLMs to generate more effective adversarial examples or to develop more robust defense mechanisms [225]. This could lead to significant advances in the field, enabling the development of more secure and resilient systems for a range of applications.

In terms of specific research questions, some potential areas of investigation include: (1) How can we develop more effective defense mechanisms against visual adversarial attacks, such as those using adversarial training or input preprocessing techniques? (2) What are the most effective attack strategies for evading detection by current defense mechanisms, and how can we develop more robust systems to counter these threats [226]? (3) How can we establish standardized benchmarks and evaluation criteria for visual adversarial attacks and defenses, and what are the key challenges and limitations of current approaches [227]? By addressing these research questions, researchers can help to create more secure and resilient systems for a range of applications, from computer vision to cybersecurity.

To address these research questions, researchers could employ a range of methodologies, including experimental evaluations, theoretical analyses, and surveys of existing literature [228]. For example, researchers could conduct experiments to evaluate the effectiveness of different defense mechanisms against various attack strategies, or develop theoretical models to analyze the robustness of different systems [229]. By using a combination of these approaches, researchers can gain a deeper understanding of the complex issues surrounding visual adversarial attacks and defenses, and develop more effective solutions to address these challenges.

Overall, the field of visual adversarial attacks and defenses is rapidly evolving, with many new challenges and opportunities emerging as a result of advances in AI and other technologies. By exploring novel attack strategies, establishing standardized benchmarks and evaluation criteria, and developing more effective defense mechanisms, researchers can help to create more secure and resilient systems for a range of applications, from computer vision to cybersecurity [230]. As the field continues to advance, it is essential to prioritize collaboration and knowledge-sharing among researchers, practitioners, and policymakers to ensure that the benefits of these advances are realized while minimizing the risks.

### 8.3 Recommendations for Researchers and Practitioners

To improve the security and robustness of computer vision systems against visual adversarial attacks in the physical world, several key recommendations can be made for researchers, practitioners, and policymakers. Building on the future research directions outlined in the previous section, it is essential to develop more robust and resilient computer vision models that can withstand various types of adversarial attacks [7]. This can be achieved by incorporating adversarial training methods, such as adversarial training with different types of attacks, into the model development process [231]. By doing so, researchers can help to create more secure and reliable systems for a range of applications, from computer vision to cybersecurity.

In addition to developing more robust models, researchers and practitioners should focus on developing defense mechanisms that can detect and mitigate adversarial attacks in real-time [232]. This can be achieved by using techniques such as input preprocessing, feature extraction, and anomaly detection [233]. Furthermore, the use of explainable AI techniques can help to identify and understand the vulnerabilities of computer vision models, making it easier to develop more robust and secure systems [234]. By leveraging these techniques, researchers and practitioners can help to promote the development and deployment of secure and robust computer vision systems.

Policymakers and industry leaders also have a crucial role to play in promoting the development and deployment of secure and robust computer vision systems [160]. This can be achieved by establishing standards and regulations for the development and deployment of computer vision systems, as well as providing funding and resources for research and development in this area [148]. Moreover, it is essential to raise awareness about the potential risks and threats associated with visual adversarial attacks in the physical world [3]. This can be achieved through education and training programs for researchers, practitioners, and policymakers, as well as through public awareness campaigns [235].

As the field of visual adversarial attacks and defenses continues to evolve, it is recommended that researchers focus on developing more advanced and sophisticated defense mechanisms against visual adversarial attacks [212]. This can include the development of novel adversarial attack detection methods, such as using machine learning-based approaches or statistical methods [236]. Additionally, researchers should explore the use of transfer learning and meta-learning techniques to improve the robustness and generalizability of computer vision models [237]. By pursuing these research directions, researchers can help to create more secure and robust computer vision systems that can withstand the evolving threats of visual adversarial attacks.

Ultimately, the development of secure and robust computer vision systems against visual adversarial attacks in the physical world will require a collaborative effort from researchers, practitioners, and policymakers. By working together, we can develop more advanced and sophisticated defense mechanisms against visual adversarial attacks and promote the development and deployment of secure and robust computer vision systems in the physical world [238]. This collaboration can be facilitated through the establishment of research collaborations, joint research projects, and industry-academia partnerships [239]. By leveraging these partnerships, we can help to create a more secure and robust computer vision ecosystem that can withstand the threats of visual adversarial attacks, as will be discussed in the concluding section.

### 8.4 Conclusion and Summary

In conclusion, this survey has provided a comprehensive overview of the current state of visual adversarial attacks and defenses in the physical world, building on the key recommendations outlined in the previous section for developing more robust and resilient computer vision models. The key findings and takeaways from this survey highlight the importance of understanding and defending against visual adversarial attacks in the physical world, as emphasized by [15], which notes that the vulnerability of deep neural networks to adversarial attacks raises concerns regarding their security and reliability. 

The survey has shown that various types of visual adversarial attacks, including pixel-level, object-level, and scene-level attacks, can be launched in the physical world, and that these attacks can have significant consequences, such as compromising the safety and security of autonomous vehicles and surveillance systems. Furthermore, the survey has highlighted the importance of developing effective defense mechanisms against visual adversarial attacks, as noted by [5], which emphasizes that certified defenses can provide strong guarantees against adversarial patches. 

The importance of a comprehensive understanding of the challenges and limitations of visual adversarial attacks and defenses in the physical world is also emphasized, as [160] notes that physical adversarial attacks can be more robust and transferable than digital attacks. This understanding is crucial for informing the development of more effective and robust defense mechanisms, as highlighted in the previous section, which discussed the need for researchers to focus on developing more advanced and sophisticated defense mechanisms against visual adversarial attacks. 

In terms of future directions, the survey suggests that there is a need for further research on developing more effective and robust defense mechanisms against visual adversarial attacks in the physical world, as noted by [86], which highlights the need for more research on adversarial attacks and defenses on 3D point cloud classification. Additionally, the survey highlights the importance of considering the societal and ethical implications of visual adversarial attacks and defenses, as [240] notes that there is a need for more research on the vulnerabilities and protections of large language models. 

Overall, this survey has shown that visual adversarial attacks and defenses in the physical world are a critical area of research, with significant implications for the safety and security of autonomous vehicles, surveillance systems, and other computer vision applications, as emphasized by [3], which notes that the threat of adversarial attacks on deep learning in computer vision is a significant concern. As the field continues to evolve, it is essential to prioritize the development of more effective and robust defense mechanisms, as well as to consider the broader societal and ethical implications of visual adversarial attacks and defenses, as highlighted by [159], which notes that there is a need for more research on developing efficient adversarial defenses for vision-language models.


## References

[1] State-of-the-art optical-based physical adversarial attacks for deep learning computer vision systems

[2] Invisible CMOS Camera Dazzling for Conducting Adversarial Attacks on Deep Neural Networks

[3] Threat of Adversarial Attacks on Deep Learning in Computer Vision: A Survey

[4] SSMI: How to Make Objects of Interest Disappear without Accessing Object Detectors?

[5] Certified Defenses for Adversarial Patches

[6] SA-Attack: Improving Adversarial Transferability of Vision-Language Pre-training Models via Self-Augmentation

[7] Adversarial Attacks in Computer Vision: Challenges and Defense Strategies

[8] Delving into the pixels of adversarial samples

[9] Fast Local Attack: Generating Local Adversarial Examples for Object Detectors

[10] Object-Attentional Untargeted Adversarial Attack

[11] Universal Physical Camouflage Attacks on Object Detectors

[12] Adversarial Attacks on Video Object Segmentation With Hard Region Discovery

[13] Adversarial Patch for 3D Local Feature Extractor

[14] PatchZero: Defending against Adversarial Patch Attacks by Detecting and  Zeroing the Patch

[15] Physical Adversarial Attacks for Camera-Based Smart Systems: Current Trends, Categorization, Applications, Research Challenges, and Future Outlook

[16] On the Real-World Adversarial Robustness of Real-Time Semantic  Segmentation Models for Autonomous Driving

[17] Adversarial Attacks on Multi-task Visual Perception for Autonomous Driving

[18] Shadows can be Dangerous: Stealthy and Effective Physical-world  Adversarial Attack by Natural Phenomenon

[19] Adversarial Robustness for Tabular Data through Cost and Utility Awareness

[20] Attention-aggregated Attack for Boosting the Transferability of Facial Adversarial Examples

[21] Improved Adversarial Robustness via Logit Regularization Methods

[22] Cross-Modal Obfuscation for Jailbreak Attacks on Large Vision-Language Models

[23] Multi-Faceted Attack: Exposing Cross-Model Vulnerabilities in Defense-Equipped Vision-Language Models

[24] MLLM-Protector: Ensuring MLLM’s Safety without Hurting Performance

[25] A Review of Adversarial Attacks in Computer Vision

[26] Adversarial Examples in Deep Learning: Characterization and Divergence

[27] Adversarial Examples for Semantic Segmentation and Object Detection

[28] Text Processing Like Humans Do: Visually Attacking and Shielding NLP Systems

[29] A Brief Comparison Between White Box, Targeted Adversarial Attacks in Deep Neural Networks

[30] Adversarial Attacks and Detection on Reinforcement Learning-Based  Interactive Recommender Systems

[31] Semantically Stealthy Adversarial Attacks against Segmentation Models

[32] Proximal Splitting Adversarial Attacks for Semantic Segmentation

[33] Defending Adversarial Attacks by Correcting logits

[34] Augmented Lagrangian Adversarial Attacks

[35] Preprocessing Techniques in Character Recognition

[36] Detecting and Isolating Adversarial Attacks Using Characteristics of the Surrogate Model Framework

[37] Survey and Taxonomy of Adversarial Reconnaissance Techniques

[38] Attacker Behaviour Forecasting Using Methods of Intelligent Data Analysis: A Comparative Review and Prospects

[39] A Survey on Adversarial Machine Learning for Code Data: Realistic Threats, Countermeasures, and Interpretations

[40] Network Security Threats and Vulnerabilities

[41] Cyber Attacks in Cloud Computing: Modelling Multi-stage Attacks using Probability Density Curves

[42] Cyber Threats of Machine Learning

[43] Validation of a vignettes-based, hands-on cybersecurity threats situational assessment tool

[44] Security Issues and Privacy in Cloud Computing

[45] The New Frontier of Cybersecurity: Emerging Threats and Innovations

[46] NLP Security and Ethics, in the Wild

[47] Characterizing and Evaluating the Reliability of LLMs against Jailbreak Attacks

[48] SoK: A Systems Perspective on Compound AI Threats and Countermeasures

[49] A Comprehensive Survey of Attack Techniques, Implementation, and Mitigation Strategies in Large Language Models

[50] Uncovering Distortion Differences: A Study of Adversarial Attacks and Machine Discriminability

[51] Evaluating the Robustness of Deep Learning Models against Adversarial Attacks: An Analysis with FGSM, PGD and CW

[52] Square Attack: a query-efficient black-box adversarial attack via random search

[53] Decision-Based Adversarial Attacks: Reliable Attacks Against Black-Box  Machine Learning Models

[54] Attacking deep networks with surrogate-based adversarial black-box methods is easy

[55] Stochastic Variance Reduced Ensemble Adversarial Attack for Boosting the Adversarial Transferability

[56] Universal Distributional Decision-based Black-box Adversarial Attack with Reinforcement Learning

[57] BO-DBA: Query-Efficient Decision-Based Adversarial Attacks via Bayesian  Optimization

[58] A Useful Taxonomy for Adversarial Robustness of Neural Networks

[59] Simple Black-Box Adversarial Perturbations for Deep Networks

[60] ShapeShifter: Robust Physical Adversarial Attack on Faster R-CNN Object Detector

[61] Adversarial Attacks on Binary Image Recognition Systems

[62] Adversarial Attacks on Medical Image Classification

[63] Decoupling Direction and Norm for Efficient Gradient-Based L2 Adversarial Attacks and Defenses

[64] PatchCleanser: Certifiably Robust Defense against Adversarial Patches  for Any Image Classifier

[65] Analyzing Adversarial Robustness of Deep Neural Networks in Pixel Space:  a Semantic Perspective

[66] A Certified Radius-Guided Attack Framework to Image Segmentation Models

[67] FooBaR: Fault Fooling Backdoor Attack on Neural Network Training

[68] Object-fabrication Targeted Attack for Object Detection

[69] Leveraging Local Patch Differences in Multi-Object Scenes for Generative Adversarial Attacks

[70] ConSeg: Contextual Backdoor Attack Against Semantic Segmentation

[71] Object-Oriented Backdoor Attack Against Image Captioning

[72] Backdoor Attack on Deep Neural Networks Triggered by Fault Injection Attack on Image Sensor Interface

[73] Influencer Backdoor Attack on Semantic Segmentation

[74] TransCAB: Transferable Clean-Annotation Backdoor to Object Detection with Natural Trigger in Real-World

[75] Effective defense against physically embedded backdoor attacks via clustering-based filtering

[76] Adversarial camera stickers: A physical camera-based attack on deep  learning systems

[77] Proactive Disentangled Modeling of Trigger-Object Pairings for Backdoor Defense

[78] Revealing Perceptible Backdoors in DNNs, Without the Training Set, via the Maximum Achievable Misclassification Fraction Statistic

[79] Marksman Backdoor: Backdoor Attacks with Arbitrary Target Class

[80] PatchAttack: A Black-box Texture-based Attack with Reinforcement Learning

[81] Training set cleansing of backdoor poisoning by self-supervised  representation learning

[82] Adequacy of the Gradient-Descent Method for Classifier Evasion Attacks

[83] Generating Out of Distribution Adversarial Attack Using Latent Space Poisoning

[84] Characterizing Adversarial Subspaces Using Local Intrinsic  Dimensionality

[85] You Only Query Once: Effective Black Box Adversarial Attacks with  Minimal Repeated Queries

[86] Adversarial Attacks and Defenses on 3D Point Cloud Classification: A Survey

[87] Minimal Adversarial Examples for Deep Learning on 3D Point Clouds

[88] epsilon-Mesh Attack: A Surface-based Adversarial Point Cloud Attack for Facial Expression Recognition

[89] On the Adversarial Robustness of Camera-based 3D Object Detection

[90] PointCA: Evaluating the Robustness of 3D Point Cloud Completion Models  Against Adversarial Examples

[91] Impact of Adversarial Examples on Deep Learning Models for Biomedical Image Segmentation

[92] DAPAS : Denoising Autoencoder to Prevent Adversarial attack in Semantic Segmentation

[93] Attack-SAM: Towards Attacking Segment Anything Model With Adversarial Examples

[94] Towards Adversarially Robust Object Detection

[95] A Survey and Evaluation of Adversarial Attacks in Object Detection

[96] Analysis and Extensions of Adversarial Training for Video Classification

[97] Recent Advances in Adversarial Training for Adversarial Robustness

[98] Adversarial Machine Learning Attacks and Defenses in Network Intrusion Detection Systems

[99] On Using Certified Training towards Empirical Robustness

[100] MAT: A Multi-strength Adversarial Training Method to Mitigate Adversarial Attacks

[101] Fortify the Guardian, Not the Treasure: Resilient Adversarial Detectors

[102] DropAttack: A Masked Weight Adversarial Training Method to Improve  Generalization of Neural Networks

[103] Efficient Adversarial Training With Transferable Adversarial Examples

[104] The Effect of Normalization in Violence Video Classification Performance

[105] Exploring Data Augmentation Methods on Social Media Corpora

[106] Text AutoAugment: Learning Compositional Augmentation Policy for Text Classification

[107] Adaptive Normalization Enhances the Generalization of Deep Learning Model in Chest X-Ray Classification

[108] Feature Selection for Machine Learning in Big Data

[109] SparCA: Sparse Compressed Agglomeration for Feature Extraction and Dimensionality Reduction

[110] Colorful Cutout: Enhancing Image Data Augmentation with Curriculum Learning

[111] Improved Technique in Arabic Handwriting Recognition

[112] PRESISTANT: Learning based assistant for data pre-processing

[113] Advanced image preprocessing and context-aware spatial decomposition for enhanced breast cancer segmentation

[114] Evaluation of Preprocessing Techniques for U-Net Based Automated Liver Segmentation

[115] Network Anomaly Detection Using Unsupervised Machine Learning :Comparative study

[116] Non-Parametric Stochastic Autoencoder Model for Anomaly Detection

[117] Identifying Financial Fraud Transactions Using Decision Tree Classifier Algorithm

[118] Credit Card Fraud Detection Using Random Forest and Local Outlier Factor

[119] Adaptive Hierarchical Certification for Segmentation using Randomized Smoothing

[120] A stacked ensemble approach with resampling techniques for highly effective fraud detection in imbalanced datasets

[121] Enhanced federated anomaly detection through autoencoders using summary statistics-based thresholding

[122] Minimizing unnecessary tax audits using multi-objective hyperparameter tuning of XGBoost with focal loss

[123] Systematic literature review on intrusion detection systems: Research trends, algorithms, methods, datasets, and limitations

[124] Machine Learning-based Classification of Indian Caste Certificates using GLCM Features

[125] Feature engineering strategies based on a One-point Crossover for fraud detection on Big Data Analytics

[126] Adaptive Regularization of Some Inverse Problems in Image Analysis

[127] Wasserstein Distributionally Robust Optimization and Variation  Regularization

[128] Robust Submodular Minimization with Applications to Cooperative Modeling

[129] Regularization via Mass Transportation

[130] Simple Stochastic Gradient Methods for Non-Smooth Non-Convex Regularized  Optimization

[131] Optimization and Optimizers for Adversarial Robustness

[132] Distributionally Robust Multiclass Classification and Applications in  Deep Image Classifiers

[133] Efficient Optimization Algorithms for Robust Principal Component Analysis and Its Variants

[134] Robust linear classification from limited training data

[135] Fast Image Recovery Using Variable Splitting and Constrained Optimization

[136] SOAR: Second-Order Adversarial Regularization

[137] Regularized Interior Point Methods for Constrained Optimization and Control

[138] Fast Nonsmooth Regularized Risk Minimization with Continuation

[139] Learning for Robust Combinatorial Optimization: Algorithm and  Application

[140] Comprehensive Overview of Optimization Techniques in Machine Learning Training

[141] Breaking the Illusion: Real-world Challenges for Adversarial Patches in Object Detection

[142] Physical Adversarial Attack Meets Computer Vision: A Decade Survey

[143] Adversarial Attacks in a Multi-view Setting: An Empirical Study of the Adversarial Patches Inter-view Transferability

[144] Quantifying the robustness of deep multispectral segmentation models against natural perturbations and data poisoning

[145] Evaluating the Robustness of Semantic Segmentation for Autonomous Driving against Real-World Adversarial Patch Attacks

[146] Robust Physical-World Attacks on Deep Learning Models

[147] Physical Adversarial Attacks on an Aerial Imagery Object Detector

[148] Navigating Threats: A Survey of Physical Adversarial Attacks on LiDAR Perception Systems in Autonomous Vehicles

[149] Empirical Evaluation of Physical Adversarial Patch Attacks Against  Overhead Object Detection Models

[150] Fool the Hydra: Adversarial Attacks against Multi-view Object Detection Systems

[151] Adversarial Attacks on Monocular Pose Estimation

[152] All You Need is RAW: Defending Against Adversarial Attacks with Camera Image Pipelines

[153] BARReL: Bottleneck Attention for Adversarial Robustness in Vision-Based  Reinforcement Learning

[154] Don't Lag, RAG: Training-Free Adversarial Detection Using RAG

[155] Adversarial Attacks on Neural Network Policies

[156] Enhancing real-world adversarial patches through 3D modeling of complex target scenes

[157] Improving Adversarial Transferability of Visual-Language Pre-training Models through Collaborative Multimodal Interaction

[158] Adversarial Attacks Against Medical Deep Learning Systems

[159] MirrorCheck: Efficient Adversarial Defense for Vision-Language Models

[160] A Survey on Physical Adversarial Attack in Computer Vision

[161] Adversarial Robustness Assessment: Why both $L_0$ and $L_\infty$ Attacks  Are Necessary

[162] Metric Learning for Adversarial Robustness

[163] Robust Models are less Over-Confident

[164] A Comprehensive Evaluation Framework for Deep Model Robustness

[165] Delving into Decision-based Black-box Attacks on Semantic Segmentation

[166] On the Efficacy of Metrics to Describe Adversarial Attacks

[167] On Evaluating Adversarial Robustness of Volumetric Medical Segmentation Models

[168] Adversarial robustness assessment: Why in evaluation both L0 and L∞ attacks are necessary

[169] Universal Perturbation Attack on Differentiable No-Reference Image- and Video-Quality Metrics

[170] Retention Score: Quantifying Jailbreak Risks for Vision Language Models

[171] AttackBench: Evaluating Gradient-based Attacks for Adversarial Examples

[172] BackdoorBench: A Comprehensive Benchmark of Backdoor Learning

[173] MultiRobustBench: Benchmarking Robustness Against Multiple Attacks

[174] TeleAI-Safety: A comprehensive LLM jailbreaking benchmark towards attacks, defenses, and evaluations

[175] FedSecurity: A Benchmark for Attacks and Defenses in Federated Learning and Federated LLMs

[176] VFLAIR: A Research Library and Benchmark for Vertical Federated Learning

[177] Benchmarking Transferable Adversarial Attacks

[178] Heterogeneous Model Combinatorial Defense Framework (HMCDF) for Adversarial Attacks

[179] Blades: A Unified Benchmark Suite for Byzantine Attacks and Defenses in Federated Learning

[180] TrojanZoo: Towards Unified, Holistic, and Practical Evaluation of Neural Backdoors

[181] GUARD:Dual-Agent based Backdoor Defense on Chain-of-Thought in Neural Code Generation

[182] Rogue Signs: Deceiving Traffic Sign Recognition with Malicious Ads and  Logos

[183] PhysGAN: Generating Physical-World-Resilient Adversarial Examples for Autonomous Driving

[184] Simple Physical Adversarial Examples against End-to-End Autonomous  Driving Models

[185] VCAT: Vulnerability-aware and Curiosity-driven Adversarial Training for Enhancing Autonomous Vehicle Robustness

[186] AdvReal: Physical adversarial patch generation framework for security evaluation of object detection systems

[187] ControlLoc: Physical-World Hijacking Attack on Visual Perception in Autonomous Driving

[188] Dirty Road Can Attack: Security of Deep Learning based Automated Lane  Centering under Physical-World Attack

[189] Sardino: Ultra-Fast Dynamic Ensemble for Secure Visual Sensing at Mobile Edge

[190] Moving target defense for embedded deep visual sensing against adversarial examples

[191] Invisible for both Camera and LiDAR: Security of Multi-Sensor Fusion based Perception in Autonomous Driving Under Physical-World Attacks

[192] Fooling Detection Alone is Not Enough: First Adversarial Attack against  Multiple Object Tracking

[193] Physical Adversarial Attacks for Surveillance: A Survey

[194] Enhancing Security in Real-Time Video Surveillance: A Deep Learning-Based Remedial Approach for Adversarial Attack Mitigation

[195] Detecting and Segmenting Adversarial Graphics Patterns from Images

[196] A Novel Adversarial Detection Method for UAV Vision Systems via Attribution Maps

[197] Preprocessing Pipelines including Block-Matching Convolutional Neural Network for Image Denoising to Robustify Deep Reidentification against Evasion Attacks

[198] Adversarial Camouflage: Hiding Physical-World Attacks With Natural Styles

[199] AdvFAS: A robust face anti-spoofing framework against adversarial examples

[200] Invisible Adversarial Attacks on Deep Learning-Based Face Recognition Models

[201] ApaNet: adversarial perturbations alleviation network for face verification

[202] FaceGuard: A Self-Supervised Defense Against Adversarial Face Images

[203] Detecting Localized Adversarial Examples: A Generic Approach using Critical Region Analysis

[204] Efficient Decision-Based Black-Box Adversarial Attacks on Face Recognition

[205] Adv-Eye: A Transfer-Based Natural Eye Makeup Attack on Face Recognition

[206] AdvFaces: Adversarial Face Synthesis

[207] Robust Physical-World Attacks on Face Recognition

[208] Adversarial Mask: Real-World Universal Adversarial Attack on Face  Recognition Model

[209] Detecting Adversarial Faces Using Only Real Face Self-Perturbations

[210] A Comprehensive Risk Analysis Method for Adversarial Attacks on Biometric Authentication Systems

[211] Adversarial Attack Vulnerability of Medical Image Analysis Systems: Unexplored Factors

[212] Chain of Attack: On the Robustness of Vision-Language Models Against Transfer-Based Adversarial Attacks

[213] Securing Visually-Aware Recommender Systems: An Adversarial Image Reconstruction and Detection Framework

[214] Dual Attention Suppression Attack: Generate Adversarial Camouflage in Physical World

[215] Effective Black-Box Multi-Faceted Attacks Breach Vision Large Language Model Guardrails

[216] Reliable evaluation of adversarial robustness with an ensemble of  diverse parameter-free attacks

[217] From Pretrain to Pain: Adversarial Vulnerability of Video Foundation Models Without Task Knowledge

[218] Attention, Please! Adversarial Defense via Activation Rectification and Preservation

[219] Evaluating Adversarial Robustness on Document Image Classification

[220] A Survey of Side-Channel Attacks on Branch Prediction Units

[221] Benchmarking Misuse Mitigation Against Covert Adversaries

[222] CTISum: A New Benchmark Dataset For Cyber Threat Intelligence Summarization

[223] BackFed: An Efficient & Standardized Benchmark Suite for Backdoor Attacks in Federated Learning

[224] Leveraging AI and Machine Learning to Decode Adversarial Tactics, Techniques, and Procedures

[225] Advancing Cyber Threat Detection with Ai: Cutting-Edge Techniques and Future Trends

[226] AttackEval: How to Evaluate the Effectiveness of Jailbreak Attacking on Large Language Models

[227] Performance Evaluation of Adversarial Attacks: Discrepancies and  Solutions

[228] A Survey on Ethical Hacking: Issues and Challenges

[229] Analysis of Complex Network Attack and Defense Game Strategies Under Uncertain Value Criterion

[230] Proactive Defense in a Converged Threat Environment: Leveraging Predictive Cyber Analytics to Safeguard the United States' Critical Infrastructure

[231] Adversarial Attack and Defence through Adversarial Training and Feature Fusion for Diabetic Retinopathy Recognition

[232] PATCHOUT: Adversarial Patch Detection and Localization using Semantic Consistency

[233] Defending Against Person Hiding Adversarial Patch Attack with a Universal White Frame

[234] Using Multiple Self-Supervised Tasks Improves Model Robustness

[235] Revisiting Physically Realizable Adversarial Object Attack against LiDAR-based Detection: Clarifying Problem Formulation and Experimental Protocols

[236] Benchmarking Adversarial Patch Selection and Location

[237] SafeMed-R1: Adversarial Reinforcement Learning for Generalizable and Robust Medical Reasoning in Vision-Language Models

[238] Adversarial Light Projection Attacks on Face Recognition Systems: A  Feasibility Study

[239] How Stealthy is Stealthy? Studying the Efficacy of Black-Box Adversarial Attacks in the Real World

[240] Exploring Vulnerabilities and Protections in Large Language Models: A Survey


