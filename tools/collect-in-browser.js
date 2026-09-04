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
 * 5. the finished rooms.json is on your clipboard each time. in the repo:
 *      pbpaste > rooms.json
 *      git add rooms.json && git commit -m "Reddit rooms" && git push
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

  if (typeof copy === 'function') copy(text);
  console.log('%c+' + added + ' new, ' + rooms.length + ' collected in total. '
    + (typeof copy === 'function' ? 'On your clipboard: pbpaste > rooms.json'
                                  : 'Copy the object logged below.'),
    'color:#080;font-weight:bold');
  console.log('%cSkipped ' + skipped + ' posts that were not plain images.', 'color:#666');
  if (typeof copy !== 'function') console.log(text);
  return payload.count;
})();
