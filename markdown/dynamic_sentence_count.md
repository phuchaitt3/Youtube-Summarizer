### Method 1: Simple Proportional Scaling (Too Basic)

You could simply take a fixed percentage of the total sentences, for example, 10%.

*   **Logic:** `count = int(total_sentences * 0.10)`
*   **Problem:** For a short text (20 sentences), this gives only 2 key sentences, which is too few. For a very long text (1000 sentences), this gives 100 key sentences, which is no longer a summary.

### Method 2: Capped Proportional Scaling (The "Best Practice")

This is the most robust and recommended approach. It calculates a percentage of the total sentences but enforces a sensible **minimum** and **maximum** count.

*   **Logic:**
    1.  Start with a base ratio (e.g., 15% of the total sentences).
    2.  If the result is less than a minimum (e.g., 7 sentences), use the minimum.
    3.  If the result is more than a maximum (e.g., 40 sentences), use the maximum.
*   **Why it's great:** It ensures even short videos get a meaningful summary, and long videos don't produce an overwhelming list of "key" points. It adapts smoothly to any video length.

### Method 3: Logarithmic Scaling (Advanced)

This method is based on the idea that the number of "key concepts" in a text doesn't grow linearly. A 20-page document doesn't have twice as many core ideas as a 10-page one; it has more detail.

*   **Logic:** `count = A * math.log(total_sentences) + B` (where A and B are constants you tune).
*   **Problem:** While theoretically sound, it's more complex and requires experimentation to find the right constants. Capped Proportional Scaling is usually just as effective and much simpler to implement.