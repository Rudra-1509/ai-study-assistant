What I Learned While Building My Study Assistant

This isn't some polished marketing pitch—just a real look at what went sideways, what I figured out, and how I actually felt building my AI study assistant.

1. The Idea vs. Reality Gap

I kicked things off with what seemed like a simple plan: upload notes, get back clear study explanations. Easy, right? I wanted LLM-quality answers, all offline, so I focused on the backend first.

In my head, the whole thing was straightforward. Input comes in—maybe a PDF, maybe an image, maybe plain text. Run it through an encoder, then a decoder, and boom: answers. But once I actually started wiring up the backend, nothing worked as neatly as I’d pictured. And then I decided to add a frontend. That opened up a whole new can of worms.

Honestly, I had no clue where to start. It felt like someone tossed me in a river and expected me to swim.

So, I stopped rushing. I dumped every idea onto paper—literally, pen and notebook—and broke the backend into small, clear steps. ChatGPT helped me sanity-check and clean up the plan. I kept tweaking the folder structure until it made sense and seemed like it could actually scale.

2. Difficulty Levels That Actually Mean Something

Here’s something I didn’t expect: if you don’t tell the decoder who it’s teaching, you get junk. It’s like asking a professor to explain something, but not telling them if the student’s a first grader or a grad student.

I knew I had to classify topics by difficulty, but I had no idea how to make it work. I started digging into embedding parameters. That part actually went okay. But deciding which parameters to use, and then figuring out how to scale and normalize them, gave me a massive headache.

I bounced ideas off ChatGPT again, and eventually landed on some decent normalization ranges that actually worked.

3. Chunking, Context, and Not Overfeeding the Model

I couldn’t just dump giant blobs of text into the model. I needed to break everything into chunks.

Surprisingly, this part was smooth. No major issues.

I set up chunk scoring using keyword density and only kept the pieces that actually mattered. The chunk size changes depending on the difficulty level, so it’s flexible.

4. Local Models, Reality Checks, and Choosing the Right Trade-off

I tried running a quantized local GGUF model (Mistral) to keep everything offline. Technically, it worked. But honestly? The results just weren’t good enough.

The outputs were hit or miss—especially when things got harder or more complex.

Turns out, getting “good enough” results from local models is way tougher than you’d think, unless you’ve got some serious hardware. For what I wanted—a real, useful study assistant—quality was way more important than staying 100% offline.

So, I switched to Cloudflare Workers AI. That gave me access to stronger models, and it was free and easy to plug in. The difference in quality and consistency was massive.

Lesson learned: good engineering is about smart trade-offs, not chasing some ideal.

5. Frontend Struggles and Owning My Weaknesses

Frontend isn’t really my thing, especially when it comes to UI and layout.

To get past that, I grabbed a React and Tailwind template, then tweaked it bit by bit. Over time, it started to look and work better. Using TypeScript and shadcn helped a ton, too.

Honestly, using a template isn’t cheating—it’s just smart.

6. When Everything Worked Locally—Then Deployment Broke Everything

Locally? Everything ran great. Then I tried to deploy with Docker, using platforms like Render and Vercel. Total disaster.

APIs failed, environments acted weird, builds broke for no clear reason. Docker on Windows crawled—it took 10-20 minutes just to get nowhere.

I spent two or three days chasing fixes. Every time I got one thing working, something else broke.

Eventually, I gave up on deployment. I decided to focus on making it rock-solid locally. That call took a huge weight off my shoulders and let me actually make progress.

7. Struggling With Prompt Engineering (Harder Than It Looks)

Problem:
Prompt engineering turned out to be one of the hardest parts of the project. Small wording changes caused big behavioral shifts. The model would sometimes ignore instructions, over-structure content, or behave slightly differently than expected.

What I learned:
Prompts are not instructions in the traditional programming sense — they are probabilistic nudges. Precision matters far more than verbosity.

How I tackled it:

Iterated on prompts dozens of times

Removed unnecessary instructions that added noise

Focused on describing behavior, not just output format

This phase taught me that prompt design is closer to system design than copywriting.

8. Realizing What I Actually Built

At some point, it hit me:

This isn’t just an app.
It’s a small, controlled ChatGPT for studying.

Not general.
Not noisy.
Not overconfident.

Just focused.

That realization made all the debugging and frustration worth it.

Final Reflection

Total time spent: ~1 month (from start to end)

***Biggest lessons***:

Prompt design is system design

Control beats cleverness

Separation of concerns matters even with AI

Good defaults are everything

Knowing when not to deploy is also a skill

This project didn’t just teach me how to use an LLM — it taught me how to engineer behavior and make pragmatic trade-offs.

And that’s something I’ll carry forward into every AI project I build.
