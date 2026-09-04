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
 * 5. a panel appears at the bottom of the page holding the finished
 *    rooms.json, with a button to download it and a button to copy it.
 *    the text is sitting there either way, so nothing about this step can
 *    fail without you seeing it.
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

  /* Put the result on the page.

     Everything quieter than this has failed at least once: copy() leaves
     the previous clipboard in place when it cannot write, and a download
     started without a click is blocked outright by chrome on some sites,
     with nothing to see either way. A panel with the text in it and two
     buttons cannot fail silently, and a click is a user gesture, which is
     what the download and clipboard APIs want anyway. */
  const old = document.getElementById('liminal-out');
  if (old) old.remove();

  const box = document.createElement('div');
  box.id = 'liminal-out';
  box.style.cssText = [
    'position:fixed', 'inset:auto 12px 12px 12px', 'z-index:2147483647',
    'background:#111', 'color:#eee', 'border:2px solid #666', 'padding:10px',
    'font:12px/1.5 -apple-system,Helvetica,Arial,sans-serif',
    'box-shadow:0 0 30px rgba(0,0,0,.6)', 'border-radius:6px'
  ].join(';');

  const head = document.createElement('div');
  head.style.cssText = 'margin-bottom:8px;font-weight:bold';
  head.textContent = rooms.length + ' rooms collected (' + added + ' new here, '
    + skipped + ' skipped). Save this as rooms.json:';

  const area = document.createElement('textarea');
  area.value = text;
  area.readOnly = true;
  area.style.cssText = 'width:100%;height:120px;box-sizing:border-box;'
    + 'font:11px/1.4 Menlo,monospace;background:#000;color:#9f9;border:1px solid #444;padding:6px';

  const row = document.createElement('div');
  row.style.cssText = 'margin-top:8px;display:flex;gap:8px;align-items:center;flex-wrap:wrap';

  const mkBtn = (label) => {
    const b = document.createElement('button');
    b.textContent = label;
    b.style.cssText = 'padding:7px 14px;font:12px -apple-system,Helvetica,sans-serif;'
      + 'background:#eee;color:#111;border:0;border-radius:4px;cursor:pointer';
    return b;
  };

  const dl = mkBtn('Download rooms.json');
  dl.onclick = () => {
    const blob = new Blob([text], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'rooms.json';
    document.body.appendChild(a);
    a.click();
    setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
    dl.textContent = 'Downloaded. Check your Downloads folder';
  };

  const cp = mkBtn('Copy to clipboard');
  cp.onclick = async () => {
    area.select();
    let ok = false;
    try { await navigator.clipboard.writeText(text); ok = true; } catch (_) {}
    if (!ok) { try { ok = document.execCommand('copy'); } catch (_) {} }
    cp.textContent = ok ? 'Copied' : 'Could not copy, press Cmd-C now';
  };

  const shut = mkBtn('Close');
  shut.onclick = () => box.remove();

  const note = document.createElement('span');
  note.style.cssText = 'color:#999';
  note.textContent = 'or click in the box, Cmd-A, Cmd-C';

  row.append(dl, cp, shut, note);
  box.append(head, area, row);
  document.body.appendChild(box);
  area.focus();
  area.select();

  console.log('%c' + rooms.length + ' rooms collected. Use the panel at the '
    + 'bottom of the page.', 'color:#080;font-weight:bold;font-size:13px');
  return payload.count;
})();
