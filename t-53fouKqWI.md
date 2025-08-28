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
* **`S50`**: So this is things like extracting the entities etc.
* **`S52`**: And it is very funny that the way that they're showing the text here is actually very reminiscent or similar to a tool that's been around for a long time that people use for labeling data for training up your own small models to do a lot of these kind of tasks.
* **`S55`**: But you can see that as people are starting to do this more and more with these big models with things like Gemini flashlight becoming so cheap etc.
* **`S58`**: It allows us to get reliable structured outputs.
* **`S63`**: And it does seem that they've made it so that it's not just going to be purely for the Gemini family of models, but you can also use it for open- source models.
* **`S65`**: So, let's jump into just how this works.
* **`S73`**: I suspect that's probably overkill for this.
* **`S78`**: So the cool thing with these in comparison to the BERT models is that the BERT models you'd have to collect a bunch of data.
* **`S81`**: It can work out what the medication names are the dosage the frequency and we can get that back in a JSON format.
* **`S84`**: And in some ways, you could think of this as being just a more polished version of something like that.
* **`S86`**: So, I've just set up a simple collab here.
* **`S89`**: Basically, you just need to pip install lang extract.

---
## Part 2: Final Summary (Abstractive with Citations)
This is a human-readable synthesis of the key sentences listed above. Each sentence includes citations that trace back to the original text.

In this video, the presenter introduces Lang Extract, a new library developed by Google to facilitate common NLP tasks such as text classification and information extraction [S1, S3, S5, S48, S50]. He explains that traditional NLP tasks, including sentiment analysis and entity recognition, were historically performed using models like BERT, which was highly effective for fine-tuning on specific tasks and was larger than previous models like LSTMs [S7, S10, S11, S18, S21, S24, S27, S29, S31, S34, S37]. However, recently, many companies have shifted away from these models, instead achieving similar results by prompting large language models like GPT-4 or Gemini Flash [S40]. In response, Google created Lang Extract to perform information extraction directly from existing text, providing structured outputs such as entities in JSON format, and it can be used with both Gemini models and open-source alternatives [S44, S48, S52, S58, S63, S86]. The library simplifies the process of extracting data like medication names, dosages, and frequencies, making it a more refined tool compared to traditional methods, with easy setup via pip installation [S73, S78, S81, S84, S89].