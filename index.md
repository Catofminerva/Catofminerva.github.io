---
title: "Ali's World"
layout: null
---

<style>
  /* General reset and retro background */
  html, body {
    margin: 0;
    padding: 0;
    background-image: url('stars.gif');
    background-repeat: repeat;
    color: #00ffea;
    font-family: "Comic Sans MS", "Courier New", "Lucida Console", "MS Sans Serif", monospace;
  }

  /* Central page container */
  .page {
    width: 760px;
    margin: 20px auto;
    border: 6px ridge #ff00ff;
    background: rgba(0, 0, 0, 0.75);
    box-shadow: 0 0 40px #ff00ff, inset 0 0 10px #00ffff;
  }

  /* Glittery page title */
  #glitter-title {
    font-size: 64px;
    text-align: center;
    color: #ff69b4;
    text-shadow: 0 0 6px #fff, 0 0 12px #ff00ff, 0 0 20px #00ffff;
    margin: 0;
    padding: 20px 10px 0;
  }

  /* Marquee banner styling */
  .marquee-wrap {
    margin: 10px 20px;
    border: 4px groove #00ffff;
    background: #000044;
  }
  marquee {
    color: #ffff00;
    font-weight: bold;
    font-size: 18px;
  }

  /* Layout structure */
  .layout {
    width: 100%;
    border-collapse: collapse;
  }
  .sidebar {
    width: 200px;
    background: #220022;
    border-right: 4px ridge #ff00ff;
    vertical-align: top;
  }
  .content {
    padding: 10px 14px 20px;
    vertical-align: top;
  }

  /* Navigation links */
  .nav a {
    display: block;
    margin: 8px;
    padding: 8px;
    border: 3px outset #00ffff;
    background: #111133;
    color: #00ffff;
    text-decoration: none;
    text-align: center;
    text-transform: uppercase;
    text-shadow: 0 0 4px #00ffff;
  }
  .nav a:hover {
    border-style: inset;
    color: #ff69b4;
    background: #330033;
  }

  /* Size and alignment for navigation icons */
  .nav-icon {
    vertical-align: middle;
    width: 30px;
    height: 30px;
    margin-right: 6px;
  }

  /* Post containers */
  .post {
    margin: 16px 0 24px;
    padding: 10px;
    border: 4px groove #ff69b4;
    background: rgba(30, 0, 30, 0.6);
  }
  .post h3 {
    margin: 0 0 6px 0;
    color: #ff69b4;
    text-shadow: 0 0 6px #ff69b4;
  }
  .post .meta {
    font-size: 12px;
    color: #ffff66;
  }

  /* Footer styling */
  .footer {
    padding: 12px;
    text-align: center;
    color: #fff;
  }
</style>

<div class="page">
  <h1 id="glitter-title">Ali's World</h1>

  <div class="marquee-wrap">
    <marquee behavior="alternate" scrollamount="6">
      ★ Welcome to Ali's cosmic webspace ★ Best viewed in Netscape 4.0 ★
    </marquee>
  </div>

  <table class="layout">
    <tr>
      <!-- Sidebar with navigation and counter -->
      <td class="sidebar">
        <div class="nav">
          <a href="index.html"><img src="cutehome.gif" alt="Home" class="nav-icon">Home</a>
          <a href="about.html"><img src="about.gif" alt="About" class="nav-icon">About</a>
          <a href="blog_posts.html"><img src="post.gif" alt="Entries" class="nav-icon">Entries</a>
          <a href="chat.html"><img src="chattt.gif" alt="Chat" class="nav-icon">Chat</a>
          <a href="coolsite.html"><img src="coollinks.gif" alt="Kool Webpages" class="nav-icon">Kool Webpages</a>
          <a href="guestbook.html"><img src="book-0037.gif" alt="Guestbook" class="nav-icon">Guestbook</a>
          <a href="books.html"><img src="catread.gif" alt="Kool Books" class="nav-icon">Kool Books</a>
          <a href="Truth2.html"><img src="math.gif" alt="Truth Table" class="nav-icon">Truth Table</a>
          <a href="oudsimulator.html">Oud Simulator</a>
          <a href="contact.html"><img src="phone.gif" alt="Contact" class="nav-icon">Contact</a>
        </div>

        <div style="text-align:center; padding:10px">
          <span style="font-size:12px; color:#ff0">You are visitor #</span>
          <span id="hitCount" style="display:inline-block; padding:4px 8px; border:3px inset #aaa; background:#000; color:#00ff00; font-family:'Courier New', monospace; letter-spacing:2px;">000001</span>
        </div>

        <div style="padding: 0 10px 12px; color:#fff; font-size:12px">
          <div><a href="#" onclick="alert('Email me!'); return false;">Email Me</a></div>
          <div style="margin-top:6px"><a href="#" onclick="alert('Guestbook coming soon!'); return false;">Sign my Guestbook</a></div>
          <div style="margin-top:6px">Last updated: <span id="lastUpdated">sometime in 1999</span></div>
        </div>
      </td>

      <!-- Main content area -->
      <td class="content">
        <div class="post">
          <h3>Welcome</h3>
          <div class="meta">1999 · Ali's cosmic home</div>
          <p>Hey there, welcome to my blog! Glad you could stop by. I've been doing some tinkering around these digital corners, and I'm thrilled to go live. There are a few things you can check out; blog posts lined up above, and more to come as I format and digitise them. Chat room is now up and fully running, encrypted and uses my personal server. You can now also check out the cool hyperlinks and books. Feedback is always welcome. Thanks again for your interest! I'm hoping you find something here that you like, and maybe even something you find slightly offensive! Oh, and don't forget to feed Zaki while you're here!</p>
        </div>

        <div class="post">
          <h3>Pet and feed Zaki</h3>
          <div class="meta">Virtual pet</div>
          <iframe width="314" height="321" scrolling="no" src="https://gifypet.neocities.org/pet/pet.html?name=Zaki&amp;dob=1698667285&amp;gender=b&amp;element=Fire&amp;pet=cat.gif&amp;map=night.gif&amp;background=https%3A%2F%2Fmedia.giphy.com%2Fmedia%2FFlodpfQUBSp20%2Fgiphy.gif&amp;tablecolor=%23000000&amp;textcolor=%238700e0" frameborder="0"></iframe>
        </div>
      </td>
    </tr>
  </table>

  <div class="footer">
    <marquee scrollamount="3" direction="right">© 1999–2000 Ali's Blog — Part of the Galactic Webring · <a href="#" onclick="alert('Prev page broken'); return false;">Prev</a> | <a href="#" onclick="alert('Next page loading...'); return false;">Next</a></marquee>
  </div>
</div>

<script>
  (function() {
    try {
      var key = 'geocities_hit_counter';
      var n = parseInt(localStorage.getItem(key) || '0', 10) + 1;
      localStorage.setItem(key, n);
      var s = String(n).padStart(6, '0');
      document.getElementById('hitCount').textContent = s;
    } catch (e) {
      // If localStorage is unavailable, do nothing.
    }
  })();

  // Display last modified date
  document.getElementById('lastUpdated').textContent = document.lastModified || '1999-08-01';
</script>
