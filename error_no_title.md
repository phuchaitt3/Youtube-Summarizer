# Extractive Summary for YouTube Video

**Source URL:** https://www.youtube.com/watch?v=t-53fouKqWI

---

Below are the most important sentences identified from the transcript. These sentences form the basis for the final abstractive summary.

* **`S1`**: Okay, so in this video I want to go through Lang Extract, a new library that's come out of Google to help us basically do a lot of standard NLP tasks.
* **`S3`**: But before we get to that, I want to talk about an interesting trend that I've been seeing of how people are doing sort of standard NLP.
* **`S5`**: I'm talking about simple things like text classification being able to do things like sentiment being able to say if a piece of text belongs to one class or one group as opposed to another.
* **`S7`**: And for a long time, a lot of these tasks were done with BERT models.
* **`S10`**: But the BERT model basically if we go back to what many people would think of as ancient history when talking about language models and transformers, the BERT model is a very different kind of model than what we've got now.
* **`S11`**: So most people talk about the transformer architecture and this is what was invented in 2017 and came out of Google.
* **`S18`**: And the BERT model was very useful at doing a lot of these standard tasks.
* **`S21`**: But the key thing here was that these BER models were really good for fine-tuning for very specific NLP tasks.
* **`S24`**: And when it came out, the B model was actually that.
* **`S27`**: So it's pretty small, but that was way bigger than what had been around with things like LSTMs and stuff like that before.
* **`S29`**: Now people ended up using different versions of this kind of thing where they would use like a distilled B.
* **`S31`**: And interestingly, at the end of last year, we saw the introduction of the modern BERT.
* **`S34`**: And in fact, even things like the original BER base model was only about 110 million parameters.
* **`S37`**: And for a long time, people were using these models in production to do various things like extracting names, extracting entities, doing things like sentiment analysis, doing things like text classification and they worked very well.
* **`S40`**: But then over the last say six months, I've started to see a whole new pattern emerge that a lot of big companies are just not using these models anymore because they're finding that they can just get the same results by wrapping the text in a prompt and then giving it to a GPT 40 Mini or a Gemini Flash or a model, something like that.
* **`S43`**: And that's what brings us to Lang Extract.
* **`S44`**: So Lang Extract is a library made by Google specifically to do these kinds of tasks with Gemini.
* **`S48`**: So what lang extract is actually built for is these tasks of doing information extraction from text that you've already got.
* **`S51`**: And the idea here is that it's not only going to give you those back, it's going to give you where they actually are in the text and allow you to run checks yourself to see that they're actually there.
* **`S58`**: It allows us to get reliable structured outputs.
* **`S60`**: And it's even been set up for doing sort of long context information extraction.
* **`S63`**: And it does seem that they've made it so that it's not just going to be purely for the Gemini family of models, but you can also use it for open- source models.
* **`S65`**: So, let's jump into just how this works.
* **`S73`**: I suspect that's probably overkill for this.
* **`S78`**: So the cool thing with these in comparison to the BERT models is that the BERT models you'd have to collect a bunch of data.
* **`S83`**: So there've been a bunch of libraries out there in the past that have used things like pyantic models to be able to get structured data out of LLMs that can do a lot of these things.
* **`S86`**: So, I've just set up a simple collab here.
* **`S89`**: Basically, you just need to pip install lang extract.
* **`S92`**: So starting off with their example, you can see that you've got a prompt that basically defines what it is that you want to extract.
* **`S94`**: You can see here they're going for characters, emotions, relationships in order of appearance.

---
## Part 2: Final Summary (Abstractive with Citations)
This is a human-readable synthesis of the key sentences listed above. Each sentence includes citations that trace back to the original text.

This video introduces Lang Extract, a new library developed by Google to facilitate common NLP tasks such as text classification and information extraction, highlighting a shift away from traditional models like BERT towards prompt-based approaches with models like GPT-4 and Gemini [S1, S3, S5, S7, S40, S43]. Historically, BERT models, which originated from the transformer architecture invented in 2017, were highly effective for fine-tuning on specific NLP tasks and were widely used in production for extracting entities, sentiment analysis, and text classification, with the original BERT base model containing around 110 million parameters [S10, S11, S18, S21, S24, S27, S29, S34, S37]. However, recently many large companies have shifted to using prompt-based methods with LLMs like GPT-4 Mini or Gemini Flash, achieving comparable results without relying on fine-tuned BERT models [S40]. In response to this trend, Google created Lang Extract to perform information extraction directly from text, providing reliable structured outputs and the ability to identify the location of extracted information within the text, even supporting long-context scenarios and compatibility with open-source models [S44, S48, S51, S58, S60, S63]. Unlike BERT, which required extensive data collection, Lang Extract simplifies the process by working with prompts, making it easier to extract characters, emotions, relationships, and other details without complex fine-tuning, as demonstrated in their example setup [S73, S78, S83, S86, S89, S92, S94].