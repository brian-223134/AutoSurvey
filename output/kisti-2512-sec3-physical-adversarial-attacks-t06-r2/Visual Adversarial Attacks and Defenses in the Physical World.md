# Visual Adversarial Attacks and Defenses in the Physical World

## 1 Introduction to Visual Adversarial Attacks

### 1.1 Definition and Goals of Visual Adversarial Attacks

Visual adversarial attacks refer to the process of crafting input data, such as images, to deceive computer vision systems into making incorrect predictions or classifications. These attacks can be launched in both digital and physical domains, and their goals can vary depending on the context and intentions of the attacker. In general, the primary objective of visual adversarial attacks is to exploit the vulnerabilities of deep learning models, which are widely used in computer vision applications, to compromise their performance and reliability [1]. This is achieved by creating adversarial examples, which are input data that have been specifically designed to cause a machine learning model to make a mistake.

The concept of adversarial examples is closely related to the idea of adding noise or perturbations to the input data, or using more sophisticated methods like generative adversarial networks (GANs) [2]. The goal of adversarial attacks is to create examples that are indistinguishable from legitimate input data but can cause the model to produce incorrect or undesirable outputs. For instance, an attacker could use visual adversarial attacks to cause a self-driving car to misrecognize a stop sign or a pedestrian, leading to potentially catastrophic consequences [3]. Similarly, in medical imaging, adversarial attacks could be used to manipulate images of tumors or other medical conditions, leading to incorrect diagnoses or treatments [4].

Visual adversarial attacks can be categorized into several types, including targeted and untargeted attacks. Targeted attacks aim to cause the model to produce a specific incorrect output, such as misclassifying a stop sign as a speed limit sign [5]. Untargeted attacks, on the other hand, aim to cause the model to produce any incorrect output, without specifying a particular target [6]. Additionally, attacks can be launched in either the digital or physical domain, depending on the context and intentions of the attacker [7]. Understanding these different types of attacks is essential for developing effective defense mechanisms to mitigate these threats.

The potential impact of visual adversarial attacks on computer vision systems is significant, and it is essential to develop effective defense strategies to mitigate these threats. Several defense strategies have been proposed, including adversarial training, input preprocessing, and robust optimization [8]. Adversarial training involves training the model on a dataset that includes adversarial examples, with the goal of improving its robustness to attacks [9]. Input preprocessing involves modifying the input data to reduce the effectiveness of adversarial attacks, such as by applying noise reduction or data augmentation techniques [10]. Robust optimization involves optimizing the model's parameters to minimize the impact of adversarial attacks, such as by using robust loss functions or regularization techniques [11]. By recognizing the potential impact of visual adversarial attacks, researchers and practitioners can work together to develop more robust and reliable computer vision systems that can withstand these attacks and provide accurate and trustworthy outputs [12]. 

In conclusion, visual adversarial attacks are a significant threat to computer vision systems, and their goals can vary depending on the context and intentions of the attacker. Understanding the concept of adversarial examples and the different types of attacks is essential for developing effective defense mechanisms to mitigate these threats, and ultimately, for ensuring the security and reliability of computer vision systems in various applications, including autonomous driving, surveillance, and medical diagnosis.

### 1.2 Importance of Studying Visual Adversarial Attacks

The importance of studying visual adversarial attacks cannot be overstated, as these attacks pose a significant threat to the security and reliability of computer vision systems. As discussed earlier, visual adversarial attacks involve the creation of subtle perturbations in input images that can cause deep learning models to misclassify or produce incorrect outputs. These attacks can have severe consequences in various applications, including autonomous driving, surveillance, and medical diagnosis. Therefore, it is crucial to understand the mechanisms of visual adversarial attacks, develop effective defenses, and ensure the security and reliability of computer vision systems.

One of the primary reasons for studying visual adversarial attacks is to understand their mechanisms and how they can be used to compromise computer vision systems. By analyzing the techniques used to generate adversarial examples, researchers can identify vulnerabilities in deep learning models and develop strategies to mitigate these vulnerabilities [8]. For instance, the [13] paper highlights the importance of understanding the attention mechanisms in deep learning models to develop more robust defenses against adversarial attacks. This understanding is essential for developing effective defense mechanisms, such as those discussed earlier, including adversarial training, input preprocessing, and robust optimization.

Another critical aspect of studying visual adversarial attacks is the development of effective defenses. Various defense mechanisms have been proposed, including adversarial training, input preprocessing, and gradient masking [9]. However, these defenses are not foolproof, and new attacks can be designed to bypass them. Therefore, it is essential to continue researching and developing more effective defenses against visual adversarial attacks. The [14] paper demonstrates the effectiveness of logit regularization methods in improving the robustness of deep learning models against adversarial attacks. Furthermore, the study of visual adversarial attacks can also inform the development of more robust and secure computer vision systems, which will be discussed in the following sections.

The study of visual adversarial attacks is also important for ensuring the security and reliability of computer vision systems in real-world applications. For example, in autonomous driving systems, visual adversarial attacks can be used to create fake traffic signs or perturb the input images to cause the system to misbehave [7]. Similarly, in surveillance systems, visual adversarial attacks can be used to create fake or perturbed images to evade detection [15]. The [16] paper highlights the vulnerability of segment anything models to adversarial attacks, which can have severe consequences in real-world applications. By understanding these vulnerabilities, researchers can design more secure and reliable systems that can withstand adversarial attacks.

Furthermore, the study of visual adversarial attacks can also have significant societal implications. As computer vision systems become increasingly ubiquitous in various aspects of our lives, the potential consequences of adversarial attacks can be severe. For example, in healthcare, adversarial attacks can be used to compromise medical imaging systems, leading to misdiagnosis or incorrect treatment [17]. Therefore, it is essential to continue researching and developing more effective defenses against visual adversarial attacks to mitigate these risks.

Finally, the study of visual adversarial attacks can also lead to new research directions and innovations in computer vision and machine learning. By understanding the mechanisms of adversarial attacks, researchers can develop new techniques and methods to improve the robustness and security of computer vision systems [18]. The [19] paper demonstrates the importance of continued research in adversarial attacks and defenses, highlighting the need for more effective and robust defenses against visual adversarial attacks. In conclusion, the study of visual adversarial attacks is crucial for understanding their mechanisms, developing effective defenses, and ensuring the security and reliability of computer vision systems. By continuing to research and develop new techniques and methods, we can improve the robustness and security of computer vision systems and mitigate the risks associated with adversarial attacks, as will be further discussed in the following sections [20], [21], and [22].

## 2 Background and Related Work

### 2.1 Existing Research on Visual Adversarial Attacks

Visual adversarial attacks have been a subject of interest in the field of computer vision and machine learning, with a growing body of research focused on understanding and mitigating these threats. The concept of visual adversarial attacks involves manipulating input images to cause machine learning models to misbehave or produce incorrect outputs. This can be achieved through various means, including adding noise or perturbations to the input images, or using more sophisticated methods such as generative adversarial networks (GANs) [23]. These attacks can have significant consequences, particularly in applications where machine learning models are used to make critical decisions, such as self-driving cars or medical diagnosis.

One of the earliest and most well-known types of visual adversarial attacks is the fast gradient sign method (FGSM) [8]. This method involves adding noise to the input image in the direction of the gradient of the loss function, which can cause the model to misclassify the image. Other types of attacks include the projected gradient descent (PGD) method [8], which is an iterative version of FGSM, and the Carlini and Wagner (C&W) method [8], which is a more sophisticated attack that uses a different optimization algorithm. In addition to these types of attacks, there are also more specialized types of visual adversarial attacks, such as physical-world attacks [7], which involve manipulating the physical environment to cause the model to misbehave.

To mitigate these types of attacks, researchers have proposed a variety of defense mechanisms, including adversarial training [8], which involves training the model on a dataset that includes adversarial examples, and input preprocessing [8], which involves modifying the input images to reduce the effectiveness of the attack. Other defense mechanisms include the use of robust optimization algorithms [14], such as logit regularization, and the use of ensemble methods [24], which involve combining the outputs of multiple models to improve robustness. Furthermore, recent research has also explored the use of multimodal models, which combine visual and textual information, to improve the robustness of machine learning models [25].

Despite these efforts, visual adversarial attacks remain a significant threat, and new types of attacks are continually being developed. For example, recent research has shown that it is possible to use GANs to generate highly realistic adversarial examples [23], and that these examples can be used to attack a wide range of machine learning models. Other research has shown that physical-world attacks can be used to manipulate the appearance of objects in the physical environment, causing models to misbehave [7]. Additionally, attacks that involve manipulating the semantics of the input images [26] can also have significant consequences. Therefore, it is essential to continue developing more effective defense mechanisms and improving our understanding of the types of attacks that are possible.

In conclusion, visual adversarial attacks are a significant threat to the security and reliability of machine learning models, and understanding and mitigating these threats is crucial for ensuring the safe and effective deployment of these models in computer vision applications. By developing more effective defense mechanisms and improving our understanding of the types of attacks that are possible, we can help to ensure the security and reliability of these systems [8]. As the field of visual adversarial attacks continues to evolve, it is essential to evaluate and benchmark these attacks and defenses to identify areas for improvement, which will be discussed in the following section [8].

### 2.2 Evaluation and Benchmarking of Visual Adversarial Attacks and Defenses

Evaluating and benchmarking visual adversarial attacks and defenses is crucial for understanding their effectiveness and identifying areas for improvement, as highlighted in the previous section [8]. The field of visual adversarial attacks has seen significant growth in recent years, with various attacks and defenses being proposed [8]. However, the lack of standardization in evaluation metrics and frameworks has made it challenging to compare the performance of different attacks and defenses [27]. To address this issue, researchers have proposed various evaluation metrics and frameworks for visual adversarial attacks and defenses, which will be discussed in this section.

One of the key challenges in evaluating visual adversarial attacks and defenses is the development of standardized evaluation metrics. To address this challenge, researchers have proposed various metrics, such as the "Retention Score" [28], which quantifies the robustness of vision-language models against jailbreak attacks. This metric takes into account the model's ability to maintain its performance under adversarial attacks and provides a comprehensive evaluation of its robustness. Similarly, the "hiPAA" metric [3] has been proposed to evaluate the performance of physical adversarial attacks, considering factors such as effectiveness, stealthiness, robustness, practicability, aesthetics, and economics.

In addition to these metrics, various evaluation frameworks have been proposed to benchmark visual adversarial attacks and defenses. For example, the "PatchMap" framework [29] provides a comprehensive evaluation of adversarial patch attacks, including their effectiveness, stealthiness, and robustness. Similarly, the "TROJANZOO" framework [30] has been proposed to evaluate the performance of neural backdoor attacks, providing a comprehensive evaluation of their effectiveness, stealthiness, and robustness. Other frameworks, such as the "Universal Perturbation Attack" [31] and the "REVAL" framework [32], have also been proposed to evaluate the performance of visual adversarial attacks and defenses.

The evaluation of visual adversarial attacks and defenses is not limited to the computer vision community. The "Chain of Attack" framework [33] has been proposed to evaluate the performance of vision-language models against transfer-based adversarial attacks, providing a comprehensive evaluation of their robustness. Similarly, the "Multi-Faceted Attack" framework [21] has been proposed to evaluate the performance of defense-equipped vision-language models against adversarial attacks, providing a comprehensive evaluation of their robustness.

In conclusion, evaluating and benchmarking visual adversarial attacks and defenses is crucial for understanding their effectiveness and identifying areas for improvement. Various evaluation metrics and frameworks have been proposed to address the lack of standardization in the field, including the "Retention Score" metric, the "hiPAA" metric, the "PatchMap" framework, the "TROJANZOO" framework, the "Universal Perturbation Attack" metric, and the "REVAL" framework [28], [3], [29], [30], [31], [32]. These metrics and frameworks provide a comprehensive evaluation of visual adversarial attacks and defenses, including their effectiveness, stealthiness, and robustness. As the field of visual adversarial attacks continues to evolve, it is essential to develop standardized evaluation metrics and frameworks to compare the performance of different attacks and defenses, which will be further discussed in the following section [8].

## 3 Types of Visual Adversarial Attacks

### 3.1 Physical Adversarial Attacks

Physical adversarial attacks refer to a type of attack where an adversary intentionally manipulates the physical environment to deceive a computer vision system [3]. These attacks are particularly concerning because they can be launched in the real world, potentially causing harm to people and property. In contrast to digital adversarial attacks, which involve manipulating digital images or data, physical adversarial attacks require an adversary to interact with the physical world, making them more challenging to detect and mitigate. 

Physical adversarial attacks can take many forms, including modifying objects or scenes to mislead a computer vision system [2]. For example, an attacker could place stickers on a stop sign to make it look like a speed limit sign to a self-driving car's computer vision system. Alternatively, an attacker could wear clothing with a specific pattern to evade detection by a surveillance system [34]. The diversity of physical adversarial attacks highlights the need for a comprehensive understanding of the threat models and mechanisms underlying these attacks.

The threat model for physical adversarial attacks typically involves an adversary with some level of access to the physical environment [35]. The adversary may be able to modify objects or scenes, or they may be able to manipulate the lighting or other environmental factors. In some cases, the adversary may even be able to compromise the computer vision system itself, allowing them to launch more sophisticated attacks [36]. Understanding the capabilities and limitations of an adversary is crucial for developing effective countermeasures against physical adversarial attacks.

Studying physical adversarial attacks is crucial because they can have significant real-world consequences [37]. For example, if an attacker can manipulate a self-driving car's computer vision system, they may be able to cause the car to crash or behave erratically. Similarly, if an attacker can evade detection by a surveillance system, they may be able to commit crimes without being caught [38]. The potential consequences of physical adversarial attacks underscore the need for researchers and practitioners to develop effective detection and response strategies.

To study physical adversarial attacks, researchers typically use a combination of theoretical and experimental approaches [39]. They may use simulations or laboratory experiments to test the effectiveness of different attack strategies, and they may also use real-world data to evaluate the impact of physical adversarial attacks on computer vision systems [40]. One of the key challenges in studying physical adversarial attacks is developing effective threat models [41]. Because physical adversarial attacks can take many forms, it is difficult to anticipate and prepare for all possible types of attacks. Additionally, the physical environment can be complex and dynamic, making it challenging to predict how an attack will play out in the real world [42].

Despite these challenges, researchers have made significant progress in understanding and mitigating physical adversarial attacks [43]. For example, they have developed techniques for detecting and responding to physical adversarial attacks, such as using machine learning algorithms to identify anomalous patterns in the physical environment [44]. They have also developed more robust computer vision systems that are less vulnerable to physical adversarial attacks [45]. As research in this area continues to evolve, it is likely that we will see the development of even more effective countermeasures against physical adversarial attacks.

In conclusion, physical adversarial attacks are a significant concern for computer vision systems, and studying these attacks is crucial for developing effective countermeasures [46]. By understanding the threat models and mechanisms of physical adversarial attacks, researchers can develop more robust computer vision systems that are less vulnerable to these types of attacks. Additionally, by developing effective detection and response strategies, researchers can help mitigate the impact of physical adversarial attacks and prevent them from causing harm in the real world [47]. As we move forward, it is essential to continue exploring the intersection of physical adversarial attacks and digital adversarial attacks, as discussed in the next section, to develop a comprehensive understanding of the threats and challenges facing computer vision systems.

### 3.2 Digital Adversarial Attacks

Digital adversarial attacks are a type of attack that involves manipulating digital images or data to deceive machine learning models, particularly those used in computer vision tasks. These attacks are designed to be imperceptible to the human eye, yet can cause significant errors in the model's predictions. In contrast to physical adversarial attacks, which involve manipulating the physical environment to deceive a computer vision system, digital adversarial attacks are launched in the digital domain. This subsection will discuss the definition, types, and differences of digital adversarial attacks from physical adversarial attacks, and explore the defenses against these attacks.

Digital adversarial attacks can be defined as the process of crafting malicious inputs that are designed to mislead machine learning models into making incorrect predictions [48]. These attacks can be launched in various forms, including image classification, object detection, and segmentation. The goal of digital adversarial attacks is to create a perturbed input that is similar to the original input, yet can cause the model to produce a different output. For instance, an attacker may add noise to an image of a stop sign to make it look like a speed limit sign to a self-driving car's computer vision system.

There are several types of digital adversarial attacks, including white-box, black-box, and gray-box attacks [49]. White-box attacks assume that the attacker has full knowledge of the model's architecture, parameters, and training data. Black-box attacks, on the other hand, assume that the attacker has no knowledge of the model's internal workings and can only observe the input and output. Gray-box attacks fall somewhere in between, where the attacker has some knowledge of the model's internal workings, but not complete knowledge. Digital adversarial attacks can be further categorized into targeted and non-targeted attacks [48]. Targeted attacks aim to mislead the model into producing a specific output, whereas non-targeted attacks aim to cause the model to produce any incorrect output.

One of the key differences between digital and physical adversarial attacks is the level of control the attacker has over the input [34]. In digital adversarial attacks, the attacker has complete control over the input and can manipulate it in any way they see fit. In physical adversarial attacks, the attacker must manipulate the physical environment in a way that can be captured by a sensor or camera, which can be more challenging. Another key difference between digital and physical adversarial attacks is the level of realism required [46]. Digital adversarial attacks can be launched in a purely digital environment, where the attacker can manipulate the input in any way they see fit. Physical adversarial attacks, on the other hand, require a level of realism, as the attacker must manipulate the physical environment in a way that can be captured by a sensor or camera.

Digital adversarial attacks have been shown to be effective against a wide range of machine learning models, including convolutional neural networks (CNNs) and recurrent neural networks (RNNs) [50]. These attacks can be launched using various techniques, including gradient-based methods and evolutionary algorithms. The effectiveness of digital adversarial attacks has significant implications for the security and reliability of machine learning models in a wide range of applications, including computer vision, natural language processing, and speech recognition. As computer vision systems become increasingly ubiquitous in the physical world, the risk of digital adversarial attacks will only continue to grow, highlighting the need for effective defenses against these attacks.

In addition to the types and differences of digital adversarial attacks, it is also essential to consider the defenses against these attacks [51]. Defenses against digital adversarial attacks can be categorized into two main types: proactive and reactive defenses. Proactive defenses aim to prevent the attack from occurring in the first place, whereas reactive defenses aim to detect and mitigate the attack after it has occurred. Proactive defenses against digital adversarial attacks include techniques such as adversarial training, where the model is trained on a dataset that includes adversarial examples [49]. This can help the model to learn to recognize and resist adversarial attacks. Another proactive defense is input validation, where the input is checked for validity and consistency before it is passed to the model.

Reactive defenses against digital adversarial attacks include techniques such as anomaly detection, where the output of the model is monitored for anomalies and inconsistencies [52]. If an anomaly is detected, the output can be flagged for further review or the model can be re-trained on a new dataset. Another reactive defense is output validation, where the output of the model is checked for validity and consistency before it is used in a downstream application. By combining proactive and reactive defenses, it is possible to develop robust and effective defenses against digital adversarial attacks.

In conclusion, digital adversarial attacks are a significant threat to the security and reliability of machine learning models, particularly those used in computer vision tasks. These attacks can be launched in various forms and can have significant implications for the security and reliability of machine learning models in a wide range of applications. By understanding the types and differences of digital adversarial attacks, and by developing effective defenses against these attacks, it is possible to mitigate the risks posed by digital adversarial attacks and ensure the security and integrity of machine learning models in the physical world. The next section will discuss hybrid adversarial attacks, which combine the strengths of both physical and digital attacks, and represent a significant threat to the security of computer vision systems [53].

### 3.3 Hybrid Adversarial Attacks

Hybrid adversarial attacks represent a significant threat to the security of computer vision systems, as they combine the strengths of both physical and digital attacks. These attacks can be particularly challenging to defend against, as they can exploit vulnerabilities in both the physical and digital domains [34]. Building on the concepts of digital and physical adversarial attacks discussed earlier, hybrid adversarial attacks can be used to create complex and sophisticated attacks that are difficult to detect and defend against.

One of the key challenges of hybrid adversarial attacks is that they can be designed to evade detection by traditional defense mechanisms. For example, an attacker may use a physical attack to create a perturbation in the input data, and then use a digital attack to exploit the vulnerability created by the physical attack [46]. This can make it difficult for defenders to detect and respond to the attack, as the attack may not be visible through traditional monitoring and detection mechanisms. Furthermore, hybrid adversarial attacks can be used to create complex and sophisticated attacks that are designed to evade detection by multiple layers of defense, such as intrusion detection systems or firewalls [54].

The potential impact of hybrid adversarial attacks on the physical world is a significant concern, as these attacks can be used to create complex and sophisticated attacks that are designed to evade detection by multiple layers of defense [55]. For instance, an attacker may use a hybrid adversarial attack to create a perturbation in the input data of a self-driving car, which could potentially cause the car to crash or behave erratically. This highlights the need for defenders to consider the potential physical consequences of hybrid adversarial attacks, and to develop defense mechanisms that can mitigate these risks.

To defend against hybrid adversarial attacks, defenders will need to develop a range of strategies and techniques that can detect and respond to these attacks. This may include the use of physical and digital defense mechanisms, such as intrusion detection systems and firewalls, as well as the development of new and innovative defense mechanisms that can detect and respond to hybrid adversarial attacks [38]. Additionally, defenders may need to consider the use of adversarial training, which involves training computer vision systems to be robust against adversarial attacks [56]. By developing these strategies and techniques, defenders can help to protect computer vision systems against the risks posed by hybrid adversarial attacks, and to ensure the security and integrity of these systems in the physical world.

In conclusion, hybrid adversarial attacks represent a significant threat to the security of computer vision systems, and defenders will need to develop a range of strategies and techniques to mitigate the risks posed by these attacks. This will require a comprehensive understanding of the vulnerabilities and weaknesses of computer vision systems, as well as the development of new and innovative defense mechanisms that can detect and respond to hybrid adversarial attacks [36]. By developing these strategies and techniques, defenders can help to protect computer vision systems against the risks posed by hybrid adversarial attacks, and to ensure the security and integrity of these systems in the physical world.

## 4 Attack Methods and Techniques

### 4.1 Optimization-based Attack Methods

Optimization-based methods have been widely used to generate visual adversarial examples, which are designed to mislead deep learning models into making incorrect predictions. These methods typically involve formulating an optimization problem, where the goal is to find the minimum perturbation that can be added to an input image to cause a misclassification. One of the most popular optimization-based methods for generating visual adversarial examples is the gradient-based method, which uses the gradient of the loss function to guide the search for the optimal perturbation [57]. This method is based on the idea that the gradient of the loss function can be used to identify the direction in which the perturbation should be added to the input image to maximize the loss. The gradient-based method has been shown to be highly effective in generating visual adversarial examples, but it can be computationally expensive and may not always converge to the optimal solution.

In addition to the gradient-based method, other optimization algorithms have been used to generate visual adversarial examples. For example, the gradient descent algorithm [58] is a popular choice for optimization-based methods, as it is simple to implement and can be highly effective in finding the optimal perturbation. However, the gradient descent algorithm can be sensitive to the choice of hyperparameters, such as the learning rate and the number of iterations. To address this issue, researchers have proposed various modifications to the gradient descent algorithm, such as the use of momentum or regularization techniques.

Furthermore, other optimization-based methods have been proposed for generating visual adversarial examples. For instance, the method of [59] uses a unified gradient regularization family to generate visual adversarial examples. This method is based on the idea that the gradient of the loss function can be used to regularize the perturbation added to the input image, which can help to improve the robustness of the generated adversarial examples. Additionally, the method of [60] uses submodular optimization to generate visual adversarial examples, while the method of [61] uses bilevel optimization to generate visual adversarial examples.

Recent studies have also focused on developing optimization-based methods that can generate visual adversarial examples that are highly transferable across different models [62]. The method of [63] uses a commonality-oriented gradient optimization method to generate visual adversarial examples that are highly transferable across different models. Similarly, the method of [64] uses a Nesterov accelerated gradient method to generate visual adversarial examples that are highly transferable across different models. These methods have shown promising results in generating visual adversarial examples that can effectively evade detection by different deep learning models.

In conclusion, optimization-based methods have been widely used to generate visual adversarial examples, which are designed to mislead deep learning models into making incorrect predictions. These methods typically involve formulating an optimization problem, where the goal is to find the minimum perturbation that can be added to an input image to cause a misclassification. By leveraging various optimization algorithms and techniques, researchers have developed effective methods for generating visual adversarial examples that can evade detection by deep learning models. As the field continues to evolve, it is likely that optimization-based methods will play an increasingly important role in the development of visual adversarial attacks, and will be used in conjunction with other methods, such as generative model-based methods, to create even more sophisticated attacks [65].

### 4.2 Generative Model-based Attack Methods

Generative model-based methods have emerged as a powerful approach for generating visual adversarial examples, offering a complementary perspective to the optimization-based methods discussed in the previous subsection. These methods leverage the capabilities of generative models, such as generative adversarial networks (GANs) and variational autoencoders (VAEs), to create realistic and diverse adversarial examples [65]. GANs, in particular, have been widely used for generating adversarial examples, consisting of two neural networks: a generator and a discriminator. The generator takes a random noise vector as input and produces a synthetic image, while the discriminator takes an image as input and outputs a probability that the image is real.

One of the key advantages of using GANs for generating adversarial examples is their ability to produce diverse and realistic images [66]. By sampling from the latent space of the generator, it is possible to generate a wide range of images that are similar to the real images in the training dataset. This diversity is particularly useful for generating adversarial examples, as it allows attackers to create a large number of unique examples that can be used to evade detection. Furthermore, the use of GANs can be combined with optimization-based methods to generate more effective adversarial examples, highlighting the potential for hybrid approaches that leverage the strengths of both methods.

VAEs, on the other hand, have also been used for generating adversarial examples [67]. VAEs consist of an encoder and a decoder, where the encoder maps the input image to a latent space, and the decoder maps the latent space back to the input image. VAEs are trained using a reconstruction loss, which encourages the decoder to produce images that are similar to the input images. By using a VAE to generate adversarial examples, attackers can create images that are similar to the real images in the training dataset, but with subtle perturbations that can evade detection. The use of VAEs can also be seen as a way to regularize the generator in GANs, highlighting the connections between different generative models.

Another approach for generating adversarial examples is to use a combination of GANs and VAEs [68]. This approach, known as a generative adversarial variational autoencoder (GA-VAE), uses a GAN to generate images and a VAE to regularize the generator. The GA-VAE is trained using a combination of the GAN loss and the VAE loss, which encourages the generator to produce images that are both realistic and diverse. This hybrid approach can be seen as a way to balance the trade-off between realism and diversity in generated adversarial examples.

In addition to GANs and VAEs, other generative models have also been used for generating adversarial examples, such as autoregressive models [69] and flow-based models [70]. These models offer alternative ways to generate adversarial examples, and can be used to create more sophisticated attacks that evade detection.

The use of generative model-based methods for generating adversarial examples has several advantages over traditional methods. First, generative models can produce highly realistic and diverse images, which can be used to evade detection. Second, generative models can be used to generate adversarial examples that are tailored to specific attack scenarios, such as attacks on image classification models. Finally, generative models can be used to generate adversarial examples that are robust to different types of defenses, such as adversarial training and input preprocessing. These advantages make generative model-based methods a powerful tool for generating visual adversarial examples, and highlight their potential for use in physical-world attacks, which will be discussed in the following subsection.

However, the use of generative model-based methods for generating adversarial examples also has several challenges. First, training generative models can be computationally expensive and require large amounts of data. Second, generative models can be sensitive to hyperparameters and require careful tuning to produce high-quality images. Finally, generative models can be vulnerable to mode collapse, where the generator produces limited variations of the same output. These challenges highlight the need for further research into the development of more effective and efficient generative model-based methods for generating adversarial examples.

In conclusion, generative model-based methods have emerged as a powerful approach for generating visual adversarial examples, offering a complementary perspective to optimization-based methods and highlighting the potential for hybrid approaches that leverage the strengths of both methods [71].

### 4.3 Physical-world Attack Methods

Physical-world attack methods are designed to generate adversarial examples that can be applied to real-world objects and scenes, posing a significant threat to the security of computer vision systems in various applications, including autonomous driving, surveillance, and robotics. As a natural extension of the generative model-based methods discussed in the previous subsection, physical-world attack methods have gained significant attention in recent years due to their potential to compromise the security of computer vision systems. In this subsection, we will discuss the different physical-world attack methods, including their strengths and weaknesses, and provide an overview of the current state of research in this area.

One of the key challenges in physical-world attack methods is to ensure that the generated adversarial examples are robust and effective in the physical world. This requires considering various factors, such as lighting conditions, viewpoints, and environmental noise, which can affect the performance of the attack. To address this challenge, researchers have proposed various methods, including the use of 3D modeling and simulation to generate adversarial examples that can be applied to real-world objects and scenes [72]. For instance, 3D modeling can be used to create virtual environments that mimic real-world scenarios, allowing attackers to test and refine their adversarial examples.

Another approach is to use physical adversarial examples that are designed to be robust to various environmental conditions. For example, [73] proposed a method to generate robust physical adversarial examples that can be applied to real-world objects and scenes. The method uses a combination of digital and physical attacks to generate adversarial examples that are robust to various environmental conditions, including lighting and viewpoints. This approach has been shown to be effective in compromising the security of computer vision systems in various applications.

In addition to these methods, researchers have also proposed various techniques to improve the effectiveness of physical-world attacks. For example, [74] proposed a method to use shadows to create stealthy and effective physical-world adversarial attacks. The method uses the natural phenomenon of shadows to create adversarial examples that are difficult to detect and can be applied to real-world objects and scenes. This approach highlights the importance of considering the physical environment when designing adversarial attacks.

Physical-world attack methods have also been applied to various applications, including autonomous driving and surveillance. For example, [75] proposed a method to evaluate the robustness of semantic segmentation models against real-world adversarial patch attacks in autonomous driving applications. The method uses a combination of digital and physical attacks to generate adversarial examples that can be applied to real-world objects and scenes. This approach demonstrates the potential of physical-world attack methods to compromise the security of computer vision systems in safety-critical applications.

Furthermore, physical-world attack methods have been used to attack various types of computer vision systems, including object detection and face recognition systems. For example, [76] proposed a method to use physical camera stickers to attack deep learning systems. The method uses a combination of digital and physical attacks to generate adversarial examples that can be applied to real-world objects and scenes. This approach highlights the vulnerability of computer vision systems to physical-world attacks.

In addition to these applications, physical-world attack methods have also been used to evaluate the security of computer vision systems in various environments, including indoor and outdoor environments. For example, [40] proposed a method to benchmark the physical-world adversarial robustness of vehicle detection systems in various environments. The method uses a combination of digital and physical attacks to generate adversarial examples that can be applied to real-world objects and scenes. This approach demonstrates the importance of evaluating the security of computer vision systems in various environments.

The development of physical-world attack methods is an ongoing area of research, with new methods and techniques being proposed regularly. For example, [77] proposed a method to generate physical-world-resilient adversarial examples for autonomous driving applications. The method uses a combination of digital and physical attacks to generate adversarial examples that can be applied to real-world objects and scenes. This approach highlights the potential of physical-world attack methods to compromise the security of computer vision systems in safety-critical applications.

In conclusion, physical-world attack methods are an important area of research in computer vision, with significant implications for the security of computer vision systems in various applications. The methods discussed in this subsection, including the use of 3D modeling and simulation, physical adversarial examples, and various techniques to improve the effectiveness of physical-world attacks, have demonstrated the potential to compromise the security of computer vision systems in various environments. As we move forward, it is essential to continue researching and developing physical-world attack methods to improve the security and robustness of computer vision systems. Recent works, such as [78], [79], and [80], have made significant contributions to this area, and we can expect to see further advancements in the future.

## 5 Defense Mechanisms and Strategies

### 5.1 Adversarial Training and Input Preprocessing

Adversarial training and input preprocessing are two popular defense mechanisms used to improve the robustness of deep neural networks against adversarial attacks. These mechanisms are crucial in preventing adversarial examples from being processed by the model, which is a key aspect of defending against visual adversarial attacks in the physical world. Adversarial training involves training a model on a dataset that includes adversarial examples, which are specifically designed to mislead the model. This approach has been shown to be effective in improving the robustness of models against various types of attacks [81]. For example, a study on the robustness of deep learning models against adversarial attacks found that adversarial training can improve the robustness of models by up to 50% [82].

One of the strengths of adversarial training is that it can be used to defend against a wide range of attacks, including white-box and black-box attacks. White-box attacks involve accessing the model's architecture and parameters, while black-box attacks involve accessing only the model's input and output. Adversarial training can be used to defend against both types of attacks by generating adversarial examples that are tailored to the specific attack [43]. Additionally, adversarial training can be used to improve the robustness of models against attacks that are designed to evade detection, such as attacks that use gradient masking or input preprocessing [8]. This is particularly important in the context of visual adversarial attacks, where attackers may use various techniques to evade detection.

However, adversarial training also has some weaknesses. One of the main weaknesses is that it can be computationally expensive, especially when generating adversarial examples for large datasets. This can make it difficult to scale up adversarial training to larger models and datasets [83]. Additionally, adversarial training can sometimes lead to a decrease in the model's accuracy on clean data, which can be a problem in applications where accuracy is critical [84]. To address these limitations, researchers have proposed various techniques to improve the effectiveness and efficiency of adversarial training, such as using transferable adversarial examples or multi-task learning.

Input preprocessing is another popular defense mechanism that involves modifying the input data before it is fed into the model. This can include techniques such as data normalization, feature scaling, and dimensionality reduction. Input preprocessing can be used to defend against adversarial attacks by reducing the impact of adversarial perturbations on the model's output [85]. For example, a study on the robustness of deep learning models against adversarial attacks found that input preprocessing can improve the robustness of models by up to 20% [86]. This approach is complementary to detection-based defense mechanisms, which aim to detect and reject adversarial examples, and can be used in conjunction with them to provide an additional layer of protection.

In addition to adversarial training and input preprocessing, there are several other defense mechanisms that can be used to improve the robustness of deep neural networks against adversarial attacks. These include techniques such as defensive distillation, which involves training a model on a distilled version of the input data [87]. Defensive distillation has been shown to be effective in improving the robustness of models against various types of attacks, including white-box and black-box attacks [88]. Another defense mechanism that can be used to improve the robustness of deep neural networks is adversarial example detection, which involves training a model to detect adversarial examples, and is closely related to the detection-based defense mechanisms discussed earlier [89].

In conclusion, adversarial training and input preprocessing are two popular defense mechanisms that can be used to improve the robustness of deep neural networks against adversarial attacks. While both mechanisms have their strengths and weaknesses, they can be used together with other defense mechanisms, such as detection-based defenses, to provide a robust defense against a wide range of attacks. By understanding the strengths and weaknesses of different defense mechanisms, researchers and practitioners can develop more effective defenses against adversarial attacks, which is critical for ensuring the security and reliability of deep learning models in a wide range of applications [90].

### 5.2 Detection-Based Defense Mechanisms

Detection-based defense mechanisms play a vital role in identifying and rejecting adversarial examples, thereby preventing them from being processed by the model. As discussed earlier, adversarial training and input preprocessing are two popular defense mechanisms used to improve the robustness of deep neural networks against adversarial attacks. However, detection-based defense mechanisms offer a complementary approach to these methods, aiming to detect the subtle differences between legitimate and adversarial inputs. 

One approach to detection-based defense is to use statistical methods to analyze the input data. For instance, [91] proposes a method that extracts high-level features from the input data and uses them to detect adversarial examples. This approach is based on the observation that adversarial examples often have different high-level features than legitimate inputs. Another statistical approach is to use density estimation methods, such as [92], which estimates the density of the input data and uses it to detect adversarial examples. These statistical methods can be used in conjunction with adversarial training and input preprocessing to provide a robust defense against adversarial attacks.

In addition to statistical methods, machine learning models can also be used to detect adversarial examples. For example, [93] proposes a method that uses a masked language model to detect adversarial examples in text classification tasks. This approach is based on the observation that adversarial examples often have different linguistic features than legitimate inputs. Similarly, [94] proposes a method that uses an ensemble of explanation techniques to detect adversarial examples. These machine learning-based approaches can be used to improve the accuracy and robustness of detection-based defense mechanisms.

Furthermore, there are also methods that use other techniques to detect adversarial examples. For instance, [95] proposes a method that uses behavioral analysis to detect adversarial examples. This approach is based on the observation that adversarial examples often exhibit different behavioral patterns than legitimate inputs. Another approach is to use frequency-based methods, such as [96], which analyzes the frequency components of the input data to detect adversarial examples. These methods can be used to detect adversarial examples that may evade detection by statistical or machine learning-based methods.

Detection-based defense mechanisms have several advantages over other types of defenses. For one, they do not require modifying the underlying model, which makes them more flexible and easier to deploy. Additionally, detection-based defenses can be used in conjunction with other defense mechanisms, such as adversarial training, to provide an additional layer of protection [89]. This is particularly important in the context of visual adversarial attacks, where attackers may use various techniques to evade detection.

However, detection-based defense mechanisms also have some limitations. For one, they may not be able to detect all types of adversarial examples, particularly those that are highly sophisticated or tailored to the specific detection mechanism. Additionally, detection-based defenses may introduce additional computational overhead, which can impact the performance of the system [97]. To address these limitations, researchers have proposed various techniques to improve the effectiveness and efficiency of detection-based defense mechanisms. For instance, [98] proposes a method that uses adversarial training to improve the robustness of detection-based defenses. Another approach is to use ensemble methods, such as [94], which combines multiple detection mechanisms to improve the overall accuracy and robustness of the defense.

In conclusion, detection-based defense mechanisms are a crucial component in the defense against adversarial examples. These mechanisms aim to detect and reject adversarial examples, preventing them from being processed by the model. While detection-based defenses have several advantages, they also have some limitations, such as the potential for false negatives and additional computational overhead. To address these limitations, researchers have proposed various techniques to improve the effectiveness and efficiency of detection-based defense mechanisms, such as adversarial training and ensemble methods [99]. As we move forward to discuss advanced defense mechanisms, it is essential to consider the role of detection-based defenses in enhancing the security and resilience of computer vision systems against visual adversarial attacks.

### 5.3 Advanced Defense Mechanisms

Advanced defense mechanisms are crucial in enhancing the security and resilience of computer vision systems against visual adversarial attacks. Building on the detection-based defense mechanisms discussed earlier, which aim to detect and reject adversarial examples, advanced defense mechanisms focus on improving the robustness of models against unknown attacks. One such mechanism is the Meta Invariance Defense [100], which aims to improve the robustness of models against unknown attacks by learning attack-invariant features. 

Another advanced defense mechanism is the use of game-theoretic approaches to model the interactions between attackers and defenders [101]. This approach can be used in conjunction with detection-based defense mechanisms to provide an additional layer of protection. In addition to these mechanisms, there are several other advanced defense approaches that have been proposed in recent years. For example, the use of machine learning and artificial intelligence to detect and respond to attacks [102] has shown significant promise. 

The SHIELD approach [103] uses large language models to detect and explain advanced persistent threats, while the Bi-Level Game-Theoretic Planning approach [104] uses game-theoretic planning to model the interactions between attackers and defenders. Other approaches include the LightDefense approach [105], which uses a lightweight uncertainty-driven defense mechanism to defend against jailbreak attacks, and the Embodied Active Defense approach [106], which uses recurrent feedback to counter adversarial patches. 

The Moving Target Defense approach [107] uses a moving target defense strategy to defend against attacks, and the use of autonomous intelligent cyber-defense agents [108] has also been proposed as a potential advanced defense mechanism. These advanced defense mechanisms can be used to defend against a wide range of attacks, including unknown attacks, advanced persistent threats, jailbreak attacks, and moving target defense attacks. 

In terms of future research directions, there are several areas that are worth exploring. One area is the development of more effective defense mechanisms that can defend against unknown attacks [100]. Another area is the use of game-theoretic approaches to model the interactions between attackers and defenders [101]. The use of machine learning and artificial intelligence to detect and respond to attacks [102] is also an area that is worth exploring. 

The development of more effective defense mechanisms that can defend against advanced persistent threats [103] is also an area that is worth exploring. The use of bi-level game-theoretic planning to model the interactions between attackers and defenders [104] is also an area that is worth exploring. The development of more effective defense mechanisms that can defend against jailbreak attacks [105] and moving target defense attacks [107] is also an area that is worth exploring. 

The use of embodied active defense to counter adversarial patches [106] and autonomous intelligent cyber-defense agents [108] is also an area that is worth exploring. In conclusion, advanced defense mechanisms are crucial in enhancing the security and resilience of computer vision systems against visual adversarial attacks. Several approaches have been proposed in recent years, including the use of meta invariance defense, game-theoretic approaches, machine learning and artificial intelligence, and autonomous intelligent cyber-defense agents. These mechanisms can be used to defend against a wide range of attacks and can be combined with detection-based defense mechanisms to provide comprehensive protection.

## 6 Applications and Case Studies

### 6.1 Autonomous Driving Systems

Autonomous driving systems have revolutionized the transportation industry, with the potential to significantly reduce accidents, improve traffic flow, and enhance the overall driving experience. However, as with any complex system, there are potential vulnerabilities that can be exploited by adversaries. Visual adversarial attacks, in particular, pose a significant threat to the safety and reliability of autonomous driving systems. In this subsection, we will explore the applications of visual adversarial attacks and defenses in autonomous driving systems, building on the concerns raised in the context of surveillance systems, where the reliability of computer vision models is crucial for maintaining public safety.

Visual adversarial attacks involve manipulating the input data to a deep neural network (DNN) in such a way that the output is misclassified or incorrect. In the context of autonomous driving, this can have serious consequences, such as causing the vehicle to misinterpret its surroundings, fail to detect obstacles, or make incorrect decisions. For example, an attacker could create a physical adversarial example, such as a specially designed sticker or patch, that can be placed on a stop sign or other traffic signal, causing the vehicle to misinterpret the signal and fail to stop [109]. This highlights the need for robust defense mechanisms to mitigate the risks associated with visual adversarial attacks in autonomous driving systems.

One of the key challenges in defending against visual adversarial attacks in autonomous driving systems is the complexity of the input data. Autonomous vehicles rely on a variety of sensors, including cameras, lidar, and radar, to perceive their surroundings. This data is then processed by DNNs to detect and respond to obstacles, traffic signals, and other hazards. However, the complexity of this data makes it difficult to detect and defend against adversarial attacks [110]. To address this challenge, researchers have explored various defense strategies, including adversarial training and detection-based defense mechanisms.

Despite these challenges, researchers have made significant progress in developing defenses against visual adversarial attacks in autonomous driving systems. One approach is to use adversarial training, which involves training the DNN on a dataset that includes adversarial examples [77]. This can help the DNN to learn to recognize and defend against adversarial attacks. Another approach is to use detection-based defense mechanisms, which involve detecting and rejecting adversarial examples [111]. These defense strategies can be applied to various autonomous driving scenarios, including lane detection, object detection, and motion forecasting.

In terms of specific applications, visual adversarial attacks and defenses have been explored in a variety of autonomous driving scenarios, including lane detection [112], object detection [113], and motion forecasting [114]. These scenarios highlight the potential risks and consequences of visual adversarial attacks and the need for effective defenses. Furthermore, researchers have also explored the use of adversarial attacks to test and evaluate the robustness of autonomous driving systems [115].

In conclusion, visual adversarial attacks pose a significant threat to the safety and reliability of autonomous driving systems. However, by developing and deploying effective defenses, such as adversarial training and detection-based defense mechanisms, we can help to mitigate this risk. Additionally, greater transparency and collaboration between researchers, industry leaders, and regulators are necessary to share knowledge and best practices for defending against visual adversarial attacks. As autonomous driving systems continue to evolve and improve, it is essential that we prioritize their safety and security, including defending against visual adversarial attacks [116]. By doing so, we can help to ensure the safe and reliable deployment of autonomous driving systems, which has the potential to revolutionize the transportation industry and improve the lives of millions of people [117]. Ultimately, the development of robust defenses against visual adversarial attacks in autonomous driving systems will be crucial for maintaining public trust and confidence in these systems, which is essential for their widespread adoption and success.

### 6.2 Surveillance Systems

Surveillance systems are a crucial component of modern security infrastructure, and their reliability is essential for maintaining public safety and preventing criminal activities. However, the increasing use of deep learning models in surveillance systems has introduced new vulnerabilities, particularly in the form of visual adversarial attacks. These attacks can compromise the accuracy and effectiveness of surveillance systems, allowing malicious individuals to evade detection or manipulate the system's output. The application of visual adversarial attacks in surveillance systems is a growing concern, as demonstrated by [34]. This survey highlights the potential risks and threats associated with physical adversarial attacks on surveillance systems, including the use of adversarial patches, glasses, or hats to evade detection.

One of the primary challenges in defending against visual adversarial attacks in surveillance systems is the lack of standardized evaluation protocols. As noted in [6], the existing literature on adversarial attacks in object detection is limited, and there is a need for a comprehensive framework to evaluate the effectiveness of different attack methodologies. To address this challenge, researchers have explored various defense strategies, including adversarial training and detection-based defense mechanisms. For instance, [113] demonstrates the effectiveness of adversarial training in improving the robustness of multi-task visual perception models against adversarial attacks. Similarly, [118] proposes a detection-based approach to identify and segment adversarial graphics patterns from images.

The application of visual adversarial attacks in surveillance systems also raises concerns about the potential for physical attacks. [7] provides a comprehensive survey of physical adversarial attacks on camera-based smart systems, including surveillance systems. Furthermore, the use of visual adversarial attacks in surveillance systems has implications for the development of future surveillance systems. [119] proposes a novel distributed video surveillance system that uses artificial intelligence and digital twins technologies to improve the security and reliability of surveillance systems.

In addition to the technical challenges, the application of visual adversarial attacks in surveillance systems also raises ethical and societal concerns. [120] emphasizes the need for ensuring the security and reliability of AI models used in military surveillance systems, highlighting the potential risks and consequences of adversarial attacks. As the field of visual adversarial attacks and defenses continues to evolve, it is essential to consider the unique challenges and requirements of surveillance systems, including the need for robust and reliable defense mechanisms. The development of effective defense strategies will be crucial for mitigating the risks associated with visual adversarial attacks in surveillance systems and ensuring the safety and security of individuals and communities.

In conclusion, the application of visual adversarial attacks in surveillance systems is a growing concern that requires immediate attention. The development of robust defense mechanisms, adversarial training, and detection-based defense mechanisms are essential for mitigating these attacks and ensuring the security and reliability of surveillance systems. As we move forward, it is crucial to continue exploring new defense strategies and considering the physical world constraints, ethical and societal concerns, and the development of future surveillance systems to address the challenges posed by visual adversarial attacks in surveillance systems, ultimately paving the way for the development of more secure and reliable autonomous driving systems and other applications that rely on computer vision models, such as healthcare systems.

### 6.3 Healthcare Applications

The applications of visual adversarial attacks and defenses in healthcare are a critical area of research, as the vulnerability of medical imaging systems to adversarial attacks can have severe consequences [121]. For instance, adversarial attacks on medical image analysis systems can lead to misdiagnosis or incorrect treatment, which can be life-threatening [17]. Therefore, it is essential to develop effective defense mechanisms to protect medical imaging systems against adversarial attacks [122].

Building on the concerns raised by the vulnerability of surveillance systems to visual adversarial attacks, the healthcare sector also faces significant challenges in mitigating these threats. Medical imaging systems, such as MRI and CT scans, are used to diagnose and treat various diseases, but they are vulnerable to adversarial attacks, which can compromise their accuracy and reliability [121]. To address this issue, researchers have proposed various defense mechanisms, including adversarial training and input preprocessing [8]. Adversarial training involves training a model on a dataset that includes adversarial examples, which can help improve the model's robustness to attacks [8]. Input preprocessing involves modifying the input data to reduce the impact of adversarial attacks [8]. For instance, a study used a convolutional autoencoder to denoise perturbed Fast Gradient Sign Method (FGSM) and Projected Gradient Descent (PGD) adversarial images, which improved the accuracy of a medical image analysis system [123].

In addition to medical image analysis, visual adversarial attacks have also been applied to medical image segmentation, which is a critical task in medical imaging [124]. Medical image segmentation models are vulnerable to adversarial attacks, which can compromise their accuracy and reliability [124]. To address this issue, researchers have proposed various defense mechanisms, including the use of non-local context encoders and adversarial training [125]. Furthermore, visual adversarial attacks have also been applied to other areas of healthcare, such as clinical decision support systems [126] and vision-language models for medical applications [127].

The development of robust defense mechanisms against visual adversarial attacks in healthcare is crucial for ensuring the accuracy and reliability of medical imaging systems. Researchers have proposed various defense mechanisms, including adversarial training, input preprocessing, and non-local context encoders [122]. These defense mechanisms can help improve the accuracy and reliability of medical imaging systems, which is essential for providing accurate diagnoses and treatments [17]. As the field of visual adversarial attacks and defenses continues to evolve, it is essential to consider the unique challenges and requirements of the healthcare sector, including the need for robust and reliable medical imaging systems.

In conclusion, the applications of visual adversarial attacks and defenses in healthcare are a critical area of research, as the vulnerability of medical imaging systems to adversarial attacks can have severe consequences [121]. The development of effective defense mechanisms, including adversarial training, input preprocessing, and non-local context encoders, is essential for protecting medical imaging systems against adversarial attacks [122]. As we move forward, it is crucial to continue exploring new defense mechanisms and strategies to mitigate the threats posed by visual adversarial attacks in healthcare, and to ensure the accuracy and reliability of medical imaging systems [17].

## 7 Challenges and Future Directions

### 7.1 Current Challenges and Limitations

Despite the significant advancements in the field of visual adversarial attacks, several challenges and limitations remain to be addressed. One of the primary concerns is the need for more robust and generalizable defenses [8]. Current defense mechanisms often focus on specific types of attacks or datasets, which can lead to a lack of transferability and generalizability to other scenarios. For instance, a defense mechanism that is effective against white-box attacks may not be effective against black-box attacks [128]. Moreover, the complexity of real-world scenarios, such as varying lighting conditions, occlusions, and diverse object shapes, can further exacerbate the challenges faced by defense mechanisms [3]. This highlights the importance of developing defense mechanisms that can adapt to diverse scenarios and attack types.

Another challenge is the trade-off between robustness and accuracy [129]. Many defense mechanisms aim to improve robustness by reducing the model's sensitivity to adversarial perturbations. However, this can often come at the cost of reduced accuracy on clean inputs. For example, a model that is highly robust to adversarial attacks may not perform as well on clean inputs as a model that is less robust [14]. This trade-off highlights the need for defense mechanisms that can balance robustness and accuracy, ensuring that the model's performance is not compromised in the process of improving its robustness.

The lack of standardized evaluation metrics and benchmarks is another limitation in the field [19]. Different studies often use different evaluation metrics and benchmarks, making it challenging to compare the effectiveness of various defense mechanisms. Furthermore, the lack of standardized metrics can lead to inconsistent and misleading results, which can hinder the development of more effective defense mechanisms. To address this challenge, there is a need for standardized evaluation metrics and benchmarks that can provide a comprehensive assessment of a defense mechanism's effectiveness.

The emergence of new attack methods and techniques also poses a significant challenge to defense mechanisms [130]. For instance, the development of more sophisticated attack methods, such as those that use generative models or reinforcement learning, can render existing defense mechanisms ineffective [131]. Moreover, the increasing use of multimodal data, such as images and text, can further complicate the development of effective defense mechanisms [132]. To stay ahead of these emerging threats, defense mechanisms must be continually updated and improved to address the latest attack methods and techniques.

The need for more efficient and scalable defense mechanisms is another challenge [133]. Many defense mechanisms, such as those that use adversarial training or input preprocessing, can be computationally expensive and require significant resources. This can limit their applicability in real-world scenarios, where computational resources may be limited. Moreover, the increasing use of deep neural networks in real-time applications, such as autonomous driving or video surveillance, requires defense mechanisms that can operate in real-time and with limited computational resources. To address this challenge, there is a need for more efficient and scalable defense mechanisms that can provide robust protection without compromising computational resources.

The development of more effective and efficient defense mechanisms against physical adversarial attacks is also a significant challenge [7]. Physical adversarial attacks, which involve manipulating the physical environment to deceive a machine learning model, can be particularly challenging to defend against. For instance, an attacker may use a physical object to block or obscure a camera's view, or use a projector to display a fake image. Defense mechanisms against physical adversarial attacks require a deep understanding of the physical environment and the potential attack vectors. To address this challenge, there is a need for more research on physical adversarial attacks and the development of defense mechanisms that can effectively counter these types of attacks.

Finally, the need for more research on the theoretical foundations of visual adversarial attacks is another challenge [134]. Despite the significant advancements in the field, the theoretical foundations of visual adversarial attacks are not yet fully understood. For instance, the reasons why deep neural networks are vulnerable to adversarial attacks are still not fully understood, and the development of more effective defense mechanisms requires a deeper understanding of the underlying theoretical principles. To address this challenge, there is a need for more research on the theoretical foundations of visual adversarial attacks, including the development of new theories and models that can provide a deeper understanding of the underlying mechanisms.

In conclusion, the field of visual adversarial attacks faces several challenges and limitations, including the need for more robust and generalizable defenses, the trade-off between robustness and accuracy, the lack of standardized evaluation metrics and benchmarks, the emergence of new attack methods and techniques, the need for more efficient and scalable defense mechanisms, the development of more effective defense mechanisms against physical adversarial attacks, and the need for more research on the theoretical foundations of visual adversarial attacks. Addressing these challenges will require significant advances in our understanding of visual adversarial attacks and the development of more effective defense mechanisms, ultimately leading to more secure and robust computer vision systems. This will pave the way for future research directions in the field, including the development of more effective and efficient defense mechanisms, the investigation of physical-world attack methods, and the exploration of novel techniques for detecting and mitigating adversarial attacks.

### 7.2 Future Research Directions

Future research directions in the field of visual adversarial attacks and defenses are vast and multifaceted, building upon the challenges and limitations identified in the previous section. One potential area of focus is the development of more effective and efficient defense mechanisms [135]. This could involve the use of novel techniques such as generative adversarial networks (GANs) and variational autoencoders (VAEs) to detect and mitigate adversarial attacks [136]. Additionally, researchers may explore the application of machine learning and artificial intelligence to improve the robustness of computer vision systems against visual adversarial attacks [137]. By addressing the trade-off between robustness and accuracy, as well as the need for more standardized evaluation metrics and benchmarks, these defense mechanisms can provide a more comprehensive approach to mitigating visual adversarial attacks.

Another promising area of research is the investigation of physical-world attack methods and their potential impacts on computer vision systems [138]. This could involve the development of new methodologies for generating adversarial examples that can be applied to real-world objects and scenes [139]. Furthermore, researchers may examine the role of human factors in visual adversarial attacks, including the potential for social engineering and phishing attacks [140]. By exploring these areas, researchers can gain a deeper understanding of the complexities of visual adversarial attacks and develop more effective defense mechanisms.

The use of blockchain technology and distributed ledger systems is another potential area of research in the field of visual adversarial attacks and defenses [141]. This could involve the development of secure and transparent systems for sharing and verifying visual data, as well as the creation of decentralized networks for detecting and mitigating adversarial attacks [142]. Additionally, researchers may explore the application of large language models (LLMs) and natural language processing (NLP) techniques to improve the robustness of computer vision systems against visual adversarial attacks [143]. These emerging technologies have the potential to provide new avenues for defending against visual adversarial attacks and improving the overall security of computer vision systems.

The development of more effective and efficient evaluation metrics and benchmarking frameworks is also a critical area of research in the field of visual adversarial attacks and defenses [144]. This could involve the creation of novel metrics and frameworks that can accurately assess the robustness of computer vision systems against visual adversarial attacks, as well as the development of more comprehensive and realistic benchmarking datasets [145]. Furthermore, researchers may examine the potential applications of visual adversarial attacks and defenses in various domains, including healthcare, finance, and transportation [146]. By developing more effective evaluation metrics and benchmarking frameworks, researchers can better understand the strengths and weaknesses of different defense mechanisms and develop more effective solutions.

In terms of specific techniques, researchers may explore the use of adversarial training and input preprocessing to improve the robustness of computer vision systems against visual adversarial attacks [147]. Additionally, the development of novel architectures and models, such as convolutional neural networks (CNNs) and recurrent neural networks (RNNs), may be investigated [148]. These techniques can provide a foundation for developing more effective defense mechanisms and improving the overall robustness of computer vision systems. As the field of visual adversarial attacks and defenses continues to evolve, it is likely that new techniques and methodologies will emerge, providing new opportunities for research and development.

Finally, researchers may examine the potential ethical and societal implications of visual adversarial attacks and defenses, including the potential for bias and discrimination in computer vision systems [149]. This could involve the development of more transparent and explainable systems, as well as the creation of novel techniques for detecting and mitigating bias and discrimination in computer vision systems [150]. By considering the ethical and societal implications of visual adversarial attacks and defenses, researchers can develop more responsible and effective solutions that prioritize the security and well-being of individuals and society. As the field continues to advance, it is essential to prioritize these considerations and develop solutions that are both effective and responsible. The future of visual adversarial attacks and defenses holds much promise, and it is likely that emerging trends and technologies will continue to shape the field in the years to come [151].

## 8 Ethical and Societal Implications

### 8.1 Introduction to Ethical Considerations

The emergence of visual adversarial attacks has significant implications for the development and deployment of computer vision systems, raising important ethical considerations that must be addressed by developers, researchers, and users alike [128]. At the heart of these considerations are concerns about privacy, the potential for misuse, and the responsibility of developers to ensure that their systems are designed and used in ways that respect human rights and dignity [152]. As computer vision systems become increasingly pervasive in our daily lives, it is essential to consider the potential risks and consequences of visual adversarial attacks and to develop strategies to mitigate them.

One of the primary ethical concerns associated with visual adversarial attacks is the potential for privacy violations [153]. Computer vision systems are capable of capturing and processing vast amounts of personal data, including images and videos that may contain sensitive information about individuals [154]. The use of visual adversarial attacks to manipulate or deceive these systems can compromise the privacy of individuals, potentially leading to harmful consequences such as identity theft, stalking, or other forms of harassment [155]. Furthermore, the potential for visual adversarial attacks to breach privacy and data protection can have broader societal implications, highlighting the need for robust privacy and data protection measures to prevent such attacks.

Another critical ethical consideration is the potential for misuse of visual adversarial attacks [156]. These attacks can be used to manipulate or deceive computer vision systems, potentially leading to harmful consequences such as financial loss, physical harm, or damage to reputation [121]. For example, an attacker could use a visual adversarial attack to manipulate a self-driving car's computer vision system, potentially causing an accident or other harm [3]. Similarly, an attacker could use a visual adversarial attack to manipulate a surveillance system, potentially allowing them to evade detection or commit a crime [118]. To mitigate these risks, developers and researchers must prioritize the development of secure and transparent computer vision systems that are resistant to visual adversarial attacks.

Developers and researchers have a responsibility to consider these ethical implications and to design and develop computer vision systems that are resistant to visual adversarial attacks [157]. This includes implementing robust security measures, such as encryption and access controls, to protect against unauthorized access or manipulation of the system [158]. It also includes designing systems that are transparent and explainable, allowing users to understand how the system is making decisions and to identify potential errors or biases [159]. By prioritizing transparency, accountability, and fairness, developers and researchers can help to ensure that computer vision systems are developed and deployed in ways that promote human well-being and respect human rights.

Moreover, the development and deployment of computer vision systems must be guided by a commitment to human rights and dignity [160]. This includes respecting the right to privacy and the right to non-discrimination, as well as ensuring that systems are designed and used in ways that promote transparency, accountability, and fairness [161]. Developers and researchers must also be aware of the potential for visual adversarial attacks to be used as a tool of social control, potentially undermining human rights and dignity [162]. Ultimately, addressing the ethical considerations associated with visual adversarial attacks requires a commitment to ongoing research and development, as well as a willingness to engage with the broader societal implications of these attacks [163]. By doing so, we can help to ensure that computer vision systems are developed and deployed in ways that promote human well-being and respect human rights [164].

### 8.2 Privacy and Data Protection

The privacy and data protection implications of visual adversarial attacks are a pressing concern, as these attacks can compromise sensitive information and infringe on individuals' right to privacy [155]. As highlighted in the previous discussion on the ethical considerations of visual adversarial attacks, the increasing use of computer vision systems in various applications, such as surveillance, healthcare, and social media, has created a vast amount of visual data that can be exploited by adversaries. The potential for visual adversarial attacks to reveal sensitive information about individuals, such as their identity, location, or activities [165], is significant, and it is essential to understand the risks and develop strategies to mitigate them.

One of the primary concerns is the potential for visual adversarial attacks to breach privacy and data protection, which can have broader societal implications [153]. For example, an attacker could use a visual adversarial attack to manipulate or distort visual data, potentially influencing public opinion or decision-making. This highlights the need for robust privacy and data protection measures to prevent such attacks and ensure the integrity of visual data. Furthermore, the lack of standardization and regulation in the development and deployment of computer vision systems has created a challenging scenario, where attackers can exploit vulnerabilities with relative ease [166].

To address these concerns, researchers have proposed various methods for protecting visual data against adversarial attacks, including differential privacy [167] and adversarial training [168]. Additionally, researchers have proposed using generative models to generate synthetic data that can be used to train models, reducing the need for sensitive real-world data [169]. These efforts underscore the importance of developing a comprehensive framework for protecting visual data against adversarial attacks, which should include technical, organizational, and regulatory measures to prevent attacks and ensure the privacy and data protection of individuals [170].

In developing such a framework, it is essential to prioritize transparency and accountability in the development and deployment of computer vision systems, ensuring that these systems are designed and used in ways that respect individual privacy and data protection rights [171]. This requires a multifaceted approach that involves not only technical solutions but also regulatory and organizational measures to prevent visual adversarial attacks and protect sensitive information. By adopting such an approach, we can ensure the integrity of visual data and protect individuals' rights in the digital age [172]. Ultimately, addressing the privacy and data protection implications of visual adversarial attacks is crucial for maintaining trust in AI systems and promoting a safe and secure digital environment, which is closely tied to the need for regulatory frameworks and accountability mechanisms that will be discussed in the following section.

### 8.3 Regulatory Frameworks and Accountability

The development and deployment of visual adversarial attacks have significant ethical and societal implications, and regulatory frameworks and accountability mechanisms are essential to ensure their responsible use. As [156] highlights, the lack of a unified regulatory framework can lead to inconsistencies in oversight, creating vulnerabilities that can be exploited at scale. This is particularly concerning in the context of visual adversarial attacks, which can compromise sensitive information and infringe on individuals' right to privacy, as discussed in the previous section.

To address these concerns, regulatory frameworks should prioritize transparency and accountability in the development and deployment of AI systems. The absence of transparency and accountability can lead to a lack of trust in AI systems, which can have far-reaching consequences. Furthermore, standards and guidelines for the development and deployment of AI systems are crucial, as highlighted by [173]. The lack of standards and guidelines can lead to inconsistent and ineffective approaches to AI governance, exacerbating the risks associated with visual adversarial attacks.

In addition to transparency and standards, regulatory frameworks should also prioritize accountability and enforcement mechanisms. The EU AI Act (EUAIA) introduces requirements for AI systems that intersect with the processes required to establish adversarial robustness. This underscores the need for regulatory frameworks to keep pace with the evolving landscape of adversarial machine learning, as noted in [90]. The development of regulatory frameworks and accountability mechanisms for visual adversarial attacks is a complex and ongoing challenge that requires careful consideration of multiple factors.

Ultimately, the development of safe and secure AI systems, including large language models and vision-language models, is a critical challenge that regulatory frameworks can help address. The protection of human rights and dignity should be a top priority in the development and deployment of visual adversarial attacks, and regulatory frameworks should be designed to safeguard these rights. By prioritizing transparency, accountability, and human rights, regulatory frameworks can play a key role in ensuring the responsible development and deployment of visual adversarial attacks, which is essential for maintaining trust in AI systems and protecting individuals' rights in the digital age.

## 9 Conclusion and Recommendations

### 9.1 Summary of Key Findings

This subsection provides a comprehensive summary of the key findings and takeaways from the survey on Visual Adversarial Attacks and Defenses in the Physical World. The survey highlights the importance of understanding visual adversarial attacks, their types, and the threat they pose to computer vision systems in the physical world. It also emphasizes the need for effective defenses and the security and reliability of computer vision systems.

The survey discusses the existing research on visual adversarial attacks, including the different types of attacks and defense mechanisms proposed to mitigate these attacks. It also evaluates and benchmarks visual adversarial attacks and defenses, introducing common metrics and evaluation frameworks used in the field. The survey categorizes and describes different types of visual adversarial attacks, including physical, digital, and hybrid attacks, explaining their methodologies and impacts.

Furthermore, the survey delves into the specifics of various attack methods and techniques used to generate visual adversarial examples. It also discusses the different defense mechanisms and strategies proposed to defend against visual adversarial attacks, including adversarial training and input preprocessing. The applications of visual adversarial attacks and defenses in various fields, such as autonomous driving systems, surveillance systems, and healthcare, are also explored.

The survey highlights the current challenges and limitations in the field of visual adversarial attacks and defenses, including the need for more robust and generalizable defenses [8]. It also proposes potential future research directions, including the development of more effective and efficient defense mechanisms. The importance of considering the ethical and societal implications of visual adversarial attacks is emphasized, including privacy concerns, potential misuse, and the responsibility of developers [113].

In terms of specific findings, the survey notes that the use of deep learning models has improved the performance of computer vision systems, but has also increased their vulnerability to visual adversarial attacks. The survey also highlights the importance of using diverse and representative datasets to train and evaluate computer vision models. To address the challenges in this field, researchers and practitioners should prioritize collaboration and knowledge sharing, such as sharing datasets, models, and evaluation metrics to facilitate the development of more robust and generalizable defense mechanisms.

In conclusion, the survey provides a comprehensive overview of the current state of research on visual adversarial attacks and defenses in the physical world. It highlights the importance of understanding the types of attacks, developing effective defenses, and considering the ethical and societal implications of these attacks. The survey also proposes potential future research directions and emphasizes the need for continued research in this field to ensure the security and reliability of computer vision systems [90].

### 9.2 Recommendations for Practitioners

As researchers and practitioners in the field of visual adversarial attacks and defenses, it is essential to consider the implications and potential applications of this technology, building upon the comprehensive summary of key findings and takeaways from the survey on Visual Adversarial Attacks and Defenses in the Physical World. The survey highlights the importance of understanding visual adversarial attacks, their types, and the threat they pose to computer vision systems in the physical world, as well as the need for effective defenses and the security and reliability of computer vision systems. Based on the current state of research, several recommendations can be made for those working in this area. Firstly, it is crucial to prioritize the development of more robust and generalizable defense mechanisms [8]. This can be achieved by exploring new architectures, such as the Self-Ensembling Vision Transformer (SEViT) [174], which has shown promising results in improving the robustness of vision models against adversarial attacks.

Another critical aspect to consider is the evaluation and benchmarking of visual adversarial attacks and defenses [29]. This can help identify the most effective attack methods and defense strategies, allowing researchers to focus on developing more robust models. Furthermore, the use of attention mechanisms, such as the Attention-aggregated Attack [24], can enhance the transferability of adversarial examples and improve the overall robustness of models. The development of more effective methods for detecting and defending against adversarial attacks is also an area of ongoing research, with techniques such as [168] showing promise in detecting and defending against adversarial attacks.

In addition to these technical recommendations, it is also essential to consider the ethical and societal implications of visual adversarial attacks and defenses [113]. For instance, the potential misuse of adversarial attacks in safety-critical applications, such as autonomous driving, highlights the need for more robust and reliable defense mechanisms. Moreover, the development of methods that can detect and defend against adversarial attacks, such as the MagDR approach [175], is crucial for ensuring the security and integrity of computer vision systems. Practitioners working on visual adversarial attacks and defenses should also be aware of the potential limitations and challenges associated with these technologies, such as the effectiveness of defense mechanisms being limited by the complexity of the attack methods [10].

To address these challenges, researchers and practitioners should prioritize collaboration and knowledge sharing, such as sharing datasets, models, and evaluation metrics to facilitate the development of more robust and generalizable defense mechanisms. The use of open-source frameworks and tools can also facilitate the development and evaluation of visual adversarial attacks and defenses. As the field of visual adversarial attacks and defenses continues to evolve, it is essential to explore the potential applications and implications of these technologies in various domains, such as healthcare [174], surveillance [113], and e-commerce [176]. By understanding the potential benefits and risks associated with these technologies, researchers and practitioners can develop more effective and robust defense mechanisms that can mitigate the potential threats and ensure the secure deployment of computer vision systems, ultimately informing future research directions in this field.

In conclusion, the development of visual adversarial attacks and defenses is a rapidly evolving field that requires careful consideration of the technical, ethical, and societal implications. By prioritizing the development of more robust and generalizable defense mechanisms, evaluating and benchmarking attack methods and defense strategies, and considering the potential applications and implications of these technologies, researchers and practitioners can contribute to the development of more secure and reliable computer vision systems [90], and pave the way for future research in this area, including the development of more sophisticated attack methods and more robust defense mechanisms, as discussed in the following section.

### 9.3 Future Research Directions

Future research in the field of visual adversarial attacks and defenses is expected to build upon the current state of knowledge and address the existing challenges. As discussed in the previous section, the development of more robust and generalizable defense mechanisms is crucial for mitigating the threats posed by visual adversarial attacks. To this end, one potential direction for future research is the development of more sophisticated attack methods, such as [177], that can effectively evade detection by current defense mechanisms. This can help identify the vulnerabilities of existing defense mechanisms and inform the development of more robust models.

Another area of research that is expected to gain significant attention is the development of more robust defense mechanisms, such as [13], that can withstand various types of attacks. The use of large language models (LLMs) in computer vision tasks is also an area of increasing interest, and research on [128] and [178] has shown that these models are vulnerable to adversarial attacks. Therefore, future research should focus on developing more robust LLMs that can withstand such attacks and exploring the potential applications of LLMs in computer vision.

In addition to these areas, research on [179] and [180] has shown that metamorphic testing can be an effective way to detect adversarial examples. Future research should explore the use of metamorphic testing in other areas of computer vision, such as object detection and segmentation, and investigate its potential in improving the robustness of computer vision systems. Furthermore, techniques such as [181] and [182] have shown promise in detecting and defending against adversarial attacks, and future research should focus on developing more robust and effective defense mechanisms.

The development of more effective methods for detecting and defending against adversarial attacks is also an area of ongoing research. Techniques such as [168] have shown promise in detecting and defending against adversarial attacks. Moreover, research on [24] has shown that attention mechanisms can be used to improve the transferability of adversarial examples, and future research should explore the use of attention mechanisms in other areas of computer vision. Additionally, research on [183] has shown that dual attention suppression can be used to generate adversarial camouflage in the physical world, and future research should explore the use of dual attention suppression in other areas of computer vision.

Finally, research on [184] has shown that visualization can be an effective way to understand and analyze adversarial attacks. As the field of visual adversarial attacks and defenses continues to evolve, it is essential to explore the use of visualization in other areas of computer vision, such as object detection and segmentation, and investigate its potential in improving the robustness of computer vision systems. The following section will provide a more in-depth discussion of the potential applications and implications of visual adversarial attacks and defenses in various domains.


## References

[1] Threat of Adversarial Attacks on Deep Learning in Computer Vision: A Survey

[2] State-of-the-art optical-based physical adversarial attacks for deep learning computer vision systems

[3] Physical Adversarial Attack Meets Computer Vision: A Decade Survey

[4] Digital Watermarking as an Adversarial Attack on Medical Image Analysis with Deep Learning

[5] Adversarial Light Projection Attacks on Face Recognition Systems: A  Feasibility Study

[6] A Survey and Evaluation of Adversarial Attacks in Object Detection

[7] Physical Adversarial Attacks for Camera-Based Smart Systems: Current Trends, Categorization, Applications, Research Challenges, and Future Outlook

[8] Adversarial Attacks in Computer Vision: Challenges and Defense Strategies

[9] Certified Defenses for Adversarial Patches

[10] Superpixel Attack - Enhancing Black-Box Adversarial Attack with Image-Driven Division Areas

[11] Robust Feature-Level Adversaries are Interpretability Tools

[12] Adversarial Evasion Attacks on Computer Vision using SHAP Values

[13] BARReL: Bottleneck Attention for Adversarial Robustness in Vision-Based  Reinforcement Learning

[14] Improved Adversarial Robustness via Logit Regularization Methods

[15] Breaking the Illusion: Real-world Challenges for Adversarial Patches in Object Detection

[16] Attack-SAM: Towards Attacking Segment Anything Model With Adversarial Examples

[17] Adversarial Attack Vulnerability of Medical Image Analysis Systems: Unexplored Factors

[18] Proactive Schemes: A Survey of Adversarial Attacks for Social Good

[19] Revisiting Transferable Adversarial Images: Systemization, Evaluation, and New Insights

[20] Adversarial Vision Challenge

[21] Multi-Faceted Attack: Exposing Cross-Model Vulnerabilities in Defense-Equipped Vision-Language Models

[22] Defense That Attacks: How Robust Models Become Better Attackers

[23] AdvFoolGen: Creating Persistent Troubles for Deep Classifiers

[24] Attention-aggregated Attack for Boosting the Transferability of Facial Adversarial Examples

[25] Investigating Vulnerabilities and Defenses Against Audio-Visual Attacks: A Comprehensive Survey Emphasizing Multimodal Models

[26] Frequency-driven Imperceptible Adversarial Attack on Semantic Similarity

[27] Benchmarking adversarial attacks and defenses for time-series data

[28] Retention Score: Quantifying Jailbreak Risks for Vision Language Models

[29] Benchmarking Adversarial Patch Selection and Location

[30] TrojanZoo: Towards Unified, Holistic, and Practical Evaluation of Neural Backdoors

[31] Universal Perturbation Attack on Differentiable No-Reference Image- and Video-Quality Metrics

[32] REVAL: A Comprehension Evaluation on Reliability and Values of Large Vision-Language Models

[33] Chain of Attack: On the Robustness of Vision-Language Models Against Transfer-Based Adversarial Attacks

[34] Physical Adversarial Attacks for Surveillance: A Survey

[35] Attack Taxonomy for Cyber-Physical System

[36] Cyber-Physical Energy Systems Security: Threat Modeling, Risk Assessment, Resources, Metrics, and Case Studies

[37] Machine Learning Security: Threats, Countermeasures, and Evaluations

[38] Defending the Defender: Adversarial Learning Based Defending Strategy for Learning Based Security Methods in Cyber-Physical Systems (CPS)

[39] A Survey on Machine-Learning Based Security Design for Cyber-Physical Systems

[40] Benchmarking the Physical-world Adversarial Robustness of Vehicle Detection

[41] Dependency-based security risk assessment for cyber-physical systems

[42] Spatially Correlated Patterns in Adversarial Images

[43] Defenses in Adversarial Machine Learning: A Survey

[44] LanCe: A Comprehensive and Lightweight CNN Defense Methodology against Physical Adversarial Attacks on Embedded Multimedia Applications

[45] DoPa: A Comprehensive CNN Detection Methodology against Physical  Adversarial Attacks

[46] Adversarial Examples in the Physical World: A Survey

[47] Robustness to Adversarial Attacks in Learning-Enabled Controllers

[48] A Survey on Adversarial Attack in the Age of Artificial Intelligence

[49] Adversarial Attacks and Defenses in Deep Learning

[50] Adversarial Attacks on Deep-Learning Based Radio Signal Classification

[51] Adversarial Learning in Statistical Classification: A Comprehensive  Review of Defenses Against Attacks

[52] Detecting Adversarial Examples - A Lesson from Multimedia Forensics

[53] Backdoor Attacks and Countermeasures on Deep Learning: A Comprehensive  Review

[54] Cyber-Physical Systems Security—A Survey

[55] Attack Anything: Blind DNNs via Universal Background Adversarial Attack

[56] A Survey on Physical Adversarial Attack in Computer Vision

[57] Adapting Step-size: A Unified Perspective to Analyze and Improve Gradient-based Methods for Adversarial Attacks

[58] Efficient Optimization Algorithms for Linear Adversarial Training

[59] A Unified Gradient Regularization Family for Adversarial Examples

[60] Discrete Adversarial Attacks and Submodular Optimization with  Applications to Text Classification

[61] Beyond backpropagation: bilevel optimization through implicit  differentiation and equilibrium propagation

[62] GNP Attack: Transferable Adversarial Examples Via Gradient Norm Penalty

[63] Boosting Adversarial Transferability via Commonality-Oriented Gradient Optimization

[64] Nesterov Accelerated Gradient and Scale Invariance for Adversarial  Attacks

[65] Generative Adversarial Networks : A Survey

[66] CVAE-GAN: Fine-Grained Image Generation through Asymmetric Training

[67] Adversarial Autoencoders

[68] On Unifying Deep Generative Models

[69] Multimodal Generative Models for Scalable Weakly-Supervised Learning

[70] Deep Quantization: Encoding Convolutional Activations with Deep Generative Model

[71] Generative AI in depth: A survey of recent advances, model variants, and real-world applications

[72] Enhancing real-world adversarial patches through 3D modeling of complex target scenes

[73] Robust Physical-World Attacks on Deep Learning Models

[74] Shadows can be Dangerous: Stealthy and Effective Physical-world  Adversarial Attack by Natural Phenomenon

[75] Evaluating the Robustness of Semantic Segmentation for Autonomous Driving against Real-World Adversarial Patch Attacks

[76] Adversarial camera stickers: A physical camera-based attack on deep  learning systems

[77] PhysGAN: Generating Physical-World-Resilient Adversarial Examples for Autonomous Driving

[78] AdvReal: Physical adversarial patch generation framework for security evaluation of object detection systems

[79] Diffusion Attack: Leveraging Stable Diffusion for Naturalistic Image Attacking

[80] Region-Wise Attack: On Efficient Generation of Robust Physical  Adversarial Examples

[81] Robustness and Security in Deep Learning: Adversarial Attacks and Countermeasures

[82] Ignition Phase : Standard Training for Fast Adversarial Robustness

[83] Efficient Adversarial Training With Transferable Adversarial Examples

[84] Instance adaptive adversarial training: Improved accuracy tradeoffs in  neural nets

[85] PCA improves the adversarial robustness of neural networks

[86] Improving Adversarial Robustness via Channel-wise Activation Suppressing

[87] Distillation as a Defense to Adversarial Perturbations Against Deep Neural Networks

[88] Extending Defensive Distillation

[89] Defending Against Adversarial Attack Towards Deep Neural Networks Via Collaborative Multi-Task Training

[90] Adversarial Attacks and Defense Mechanisms in Machine Learning: A Structured Review of Methods, Domains, and Open Challenges

[91] Robust Adversarial Example Detection Algorithm Based on High-Level Feature Differences

[92] Detection of Word Adversarial Examples in Text Classification: Benchmark and Baseline via Robust Density Estimation

[93] Masked Language Model Based Textual Adversarial Example Detection

[94] ExAD: An Ensemble Approach for Explanation-based Adversarial Detection

[95] The Taboo Trap: Behavioural Detection of Adversarial Samples

[96] Frequency Centric Defense Mechanisms against Adversarial Examples

[97] Adversarial Example Devastation and Detection on Speech Recognition System by Adding Random Noise

[98] Iron Sharpens Iron: Defending Against Attacks in Machine-Generated Text Detection with Adversarial Training

[99] CuRTAIL: ChaRacterizing and Thwarting AdversarIal Deep Learning

[100] Meta Invariance Defense Towards Generalizable Robustness to Unknown Adversarial Attacks

[101] DEFENSE-ATTACK INTERACTION OVER OPTIMALLY DESIGNED DEFENSE SYSTEMS VIA GAMES AND RELIABILITY

[102] Machine learning and AI for security mechanisms: A Systematic Literature Review Using a PRISMA Framework

[103] SHIELD: APT Detection and Intelligent Explanation Using LLM

[104] Bi-Level Game-Theoretic Planning of Cyber Deception for Cognitive Arbitrage

[105] LightDefense: A Lightweight Uncertainty-Driven Defense against Jailbreaks via Shifted Token Distribution

[106] Embodied Active Defense: Leveraging Recurrent Feedback to Counter Adversarial Patches

[107] Moving Target Defense Techniques: A Survey

[108] When Autonomous Intelligent Goodware Will Fight Autonomous Intelligent Malware: A Possible Future of Cyber Defense

[109] Rogue Signs: Deceiving Traffic Sign Recognition with Malicious Ads and  Logos

[110] Adversarial Attack and Defense of YOLO Detectors in Autonomous Driving  Scenarios

[111] Real-Time Robust Video Object Detection System Against Physical-World Adversarial Attacks

[112] Dirty Road Can Attack: Security of Deep Learning based Automated Lane  Centering under Physical-World Attack

[113] Adversarial Attacks on Multi-task Visual Perception for Autonomous Driving

[114] Attacking Motion Planners Using Adversarial Perception Errors

[115] Evaluating Adversarial Attacks on Driving Safety in Vision-Based Autonomous Vehicles

[116] Towards Transferable Attacks Against Vision-LLMs in Autonomous Driving with Typography

[117] Adversarial Driving: Attacking End-to-End Autonomous Driving

[118] Detecting and Segmenting Adversarial Graphics Patterns from Images

[119] AiWatch: A Distributed Video Surveillance System Using Artificial Intelligence and Digital Twins Technologies

[120] Securing AI Models Against Adversarial Attacks in Military Surveillance Systems

[121] Adversarial Attacks Against Medical Deep Learning Systems

[122] A Survey on Adversarial Deep Learning Robustness in Medical Image Analysis

[123] Auto encoder-based defense mechanism against popular adversarial attacks in deep learning

[124] Impact of Adversarial Examples on Deep Learning Models for Biomedical Image Segmentation

[125] Non-Local Context Encoder: Robust Biomedical Image Segmentation against Adversarial Attacks

[126] MedAttacker: Exploring Black-Box Adversarial Attacks on Risk Prediction Models in Healthcare

[127] Adversarial prompt and fine-tuning attacks threaten medical large language models

[128] Transferable Adversarial Attacks on Black-Box Vision-Language Models

[129] How robust accuracy suffers from certified training with convex relaxations

[130] SNEAK: Synonymous Sentences-Aware Adversarial Attack on Natural Language  Video Localization

[131] Scratch that! An Evolution-based Adversarial Attack against Neural  Networks

[132] Towards Adversarial Attack on Vision-Language Pre-training Models

[133] A Data Augmentation-based Defense Method Against Adversarial Attacks in Neural Networks

[134] Is current research on adversarial robustness addressing the right problem?

[135] A Survey on Moving Target Defense: Intelligently Affordable, Optimized and Self-Adaptive

[136] Toward Proactive, Adaptive Defense: A Survey on Moving Target Defense

[137] The Impact of Network Design Interventions on the Security of Interdependent Systems

[138] Proactive Defense in a Converged Threat Environment: Leveraging Predictive Cyber Analytics to Safeguard the United States' Critical Infrastructure

[139] Enhancing reconnaissance security: a 2-tier deception-driven model approach (2TDDSM)

[140] Developing a Multi-Layered Defence System to Safeguard Data against Phishing Attacks

[141] Blockchain-Enhanced Privacy Protection in Social Network Research and Applications

[142] Using Chia Blockchain Technology for Department of Defense Systems

[143] JailbreakZoo: Survey, Landscapes, and Horizons in Jailbreaking Large Language and Vision-Language Models

[144] A Comprehensive Survey on the Security of Smart Grid: Challenges, Mitigations, and Future Research Opportunities

[145] Large language models in 6G security: challenges and opportunities

[146] The Role of Cybersecurity in Strengthening Government Security Sectors: A Systematic Literature Review

[147] AI-powered threat detection: Opportunities and limitations in modern cyber defense

[148] Machine learning -based decision support framework for CBRN protection☆

[149] The Shadow of Fraud: The Emerging Danger of AI-powered Social Engineering and its Possible Cure

[150] Shielding Against Social Engineering Threats: A Counterintelligence Approach

[151] Emerging Trends in Cybersecurity: A Holistic View on Current Threats, Assessing Solutions, and Pioneering New Frontiers

[152] The Ethics of Interaction: Mitigating Security Threats in LLMs

[153] The Phantom Menace: Unmasking Privacy Leakages in Vision-Language Models

[154] Ethical Challenges in Computer Vision: Ensuring Privacy and Mitigating Bias in Publicly Available Datasets

[155] Visual Content Privacy Protection: A Survey

[156] Governance Considerations of Adversarial Attacks on AI Systems

[157] Ethical Hacking and Penetration Testing: Securing Digital Assets and Networks

[158] LDP-Feat: Image Features with Local Differential Privacy

[159] AI Ethics—A Bird’s Eye View

[160] Ethical Considerations in Artificial Intelligence: A Comprehensive Disccusion from the Perspective of Computer Vision

[161] A Review of Value-Conflicts in Cybersecurity

[162] Balancing privacy rights and surveillance analytics: a decision process guide

[163] AI Integrity Solutions for Deepfake Identification and Prevention

[164] Applying Standards to Advance Upstream & Downstream Ethics in Large Language Models

[165] Who Can See Through You? Adversarial Shielding Against VLM-Based Attribute Inference Attacks

[166] Evaluating Differentially Private Generative Adversarial Networks Over Membership Inference Attack

[167] Differentially Private and Adversarially Robust Machine Learning: An Empirical Evaluation

[168] AdvAttackVis: An Adversarial Attack Visualization System for Deep Neural Networks

[169] Training face verification models from generated face identity data

[170] Privacy in Practice: Private COVID-19 Detection in X-Ray Images

[171] Quantifying Privacy Risks of Prompts in Visual Prompt Learning

[172] Is Homomorphic Encryption-Based Deep Learning Secure Enough?

[173] Watermarking Without Standards Is Not AI Governance

[174] Self-Ensembling Vision Transformer (SEViT) for Robust Medical Image Classification

[175] MagDR: Mask-guided Detection and Reconstruction for Defending Deepfakes

[176] Securing Visually-Aware Recommender Systems: An Adversarial Image Reconstruction and Detection Framework

[177] PG-Attack: A Precision-Guided Adversarial Attack Framework Against Vision Foundation Models for Autonomous Driving

[178] Improving Adversarial Transferability of Visual-Language Pre-training Models through Collaborative Multimodal Interaction

[179] Metamorphic Detection of Adversarial Examples in Deep Learning Models with Affine Transformations

[180] Enhancing Cross-task Black-Box Transferability of Adversarial Examples  with Dispersion Reduction

[181] Detecting Adversarial Patches with Class Conditional Reconstruction  Networks

[182] Defending Against Person Hiding Adversarial Patch Attack with a Universal White Frame

[183] Dual Attention Suppression Attack: Generate Adversarial Camouflage in Physical World

[184] Adv-Eye: A Transfer-Based Natural Eye Makeup Attack on Face Recognition


