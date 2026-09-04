/* Collect r/LiminalSpace rooms from your own browser.
 *
 * Reddit's API is behind a builder policy now and refuses scripts, but it
 * still serves pages to you, logged in, in a normal browser. So the
 * browser does the collecting.
 *
 * 1. open  https://old.reddit.com/r/LiminalSpace/top/?t=year&limit=100
 * 2. open the console: Option-Command-J in Chrome, Option-Command-C in Safari
 *    (Chrome asks you to type "allow pasting" the first time)
 * 3. paste this whole file, press return
 * 4. repeat on as many listings as you like. it remembers what it has:
 *      .../top/?t=all&limit=100
 *      .../top/?t=month&limit=100
 *      .../hot/?limit=100
 *      .../new/?limit=100
 * 5. it downloads rooms.json to your Downloads folder, and also puts it on
 *    the clipboard if the console allows that. the download is the one to
 *    trust: a clipboard can still be holding whatever you copied last,
 *    and pasting that over rooms.json is how the file ends up full of
 *    something else.
 *
 *    then, in the browser: github.com/<you>/<repo> -> Add file ->
 *    Upload files -> drag rooms.json in -> Commit changes. A file of the
 *    same name replaces the one that is there.
 *
 * old.reddit is deliberate: every post there carries the real image url in
 * a data attribute, while the modern site renders signed thumbnail urls
 * that expire and would leave the page full of dead frames in a month.
 */
(() => {
  const STORE = 'liminal_rooms_collected';
  const IMAGE = /^https:\/\/i\.redd\.it\/[\w.\-]+\.(jpg|jpeg|png|webp)$/i;

  let held = {};
  try { held = JSON.parse(localStorage.getItem(STORE) || '{}'); } catch (_) {}

  const posts = document.querySelectorAll('#siteTable .thing, .sitetable .thing');
  if (!posts.length) {
    console.log('%cNo posts found. Are you on old.reddit.com?', 'color:#c00');
    return;
  }

  let added = 0, skipped = 0;
  posts.forEach(el => {
    const d = el.dataset || {};
    const url = d.url || '';
    if (!IMAGE.test(url)) { skipped++; return; }
    if (d.nsfw === 'true' || d.promoted === 'true') { skipped++; return; }
    if (held[url]) return;

    const titleEl = el.querySelector('a.title');
    const stamp = el.querySelector('time');
    held[url] = {
      i: d.fullname || url,
      u: url,
      t: (titleEl ? titleEl.textContent : '').trim().slice(0, 180),
      a: 'u/' + (d.author || 'unknown'),
      p: 'https://www.reddit.com' + (d.permalink || ''),
      d: stamp ? (stamp.getAttribute('datetime') || '').slice(0, 10) : '',
      s: 'r/LiminalSpace',
      l: ''
    };
    added++;
  });

  try { localStorage.setItem(STORE, JSON.stringify(held)); } catch (_) {}

  const rooms = Object.values(held);
  const payload = {
    source: 'reddit',
    subreddit: 'LiminalSpace',
    generated: new Date().toISOString().replace(/\.\d+Z$/, 'Z'),
    note: 'collected in a browser. photographs stay on reddit servers and every room links its thread.',
    count: rooms.length,
    rooms: rooms
  };
  const text = JSON.stringify(payload, null, 1);

  /* Download it as a file. The clipboard is not reliable here: copy()
     is a console convenience, it fails quietly when the page has not got
     focus, and it leaves whatever you copied last sitting there looking
     exactly like success. A file on disk cannot be mistaken for one. */
  let saved = false;
  try {
    const blob = new Blob([text], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'rooms.json';
    document.body.appendChild(a);
    a.click();
    setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
    saved = true;
  } catch (e) {
    console.log('%ccould not download: ' + e.message, 'color:#c00');
  }

  try { if (typeof copy === 'function') copy(text); } catch (_) {}

  console.log('%c+' + added + ' new. ' + rooms.length + ' rooms collected in total.',
    'color:#080;font-weight:bold;font-size:13px');
  console.log(saved
    ? '%crooms.json is in your Downloads folder. Upload that file to the repo.'
    : '%cthe download did not start. copy the text logged below into rooms.json.',
    'color:#080');
  console.log('%cskipped ' + skipped + ' posts that were not plain images.', 'color:#666');
  if (!saved) console.log(text);
  return payload.count;
})();
