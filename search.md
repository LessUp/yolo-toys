---
layout: default
title: "搜索 / Search"
description: "搜索 YOLO-Toys 文档 / Search YOLO-Toys documentation"
permalink: /search/
nav_order: 2
---

# 搜索文档 / Search Documentation

<div class="search-container">
  <div id="search-box">
    <input type="text" class="search-input" placeholder="输入关键词搜索... / Type to search..." autocomplete="off">
    <kbd>Ctrl</kbd> + <kbd>K</kbd>
  </div>

  <div id="search-results">
    <!-- Search results will be populated by Just The Docs search -->
  </div>

  <div id="search-no-results" style="display: none;">
    <p>没有找到结果 / No results found.</p>
    <p>尝试使用英文关键词或浏览 <a href="{{ site.baseurl }}/docs/">文档索引</a></p>
  </div>

  <div class="search-tips" style="margin-top: 3rem; padding: 1.5rem; background-color: rgba(79, 70, 229, 0.05); border-radius: 8px;">
    <h3>搜索技巧 / Search Tips</h3>
    <ul>
      <li><strong>精确匹配:</strong> 使用引号搜索精确短语，如 "WebSocket"</li>
      <li><strong>英文关键词:</strong> 技术术语建议用英文，如 "inference", "detection", "handler"</li>
      <li><strong>函数名:</strong> 直接搜索函数名，如 <code>infer()</code>, <code>load_model()</code></li>
      <li><strong>模块名:</strong> 搜索模块名，如 "model_manager", "routes"</li>
    </ul>
  </div>
</div>

<script>
// Custom search enhancement
document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.querySelector('.search-input');
  const searchResults = document.getElementById('search-results');
  const noResults = document.getElementById('search-no-results');

  // Focus search input on page load
  if (searchInput) {
    searchInput.focus();

    // Add clear button
    const clearBtn = document.createElement('button');
    clearBtn.className = 'search-clear';
    clearBtn.innerHTML = '✕';
    clearBtn.style.cssText = 'position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: none; border: none; cursor: pointer; font-size: 18px; color: #666;';
    clearBtn.onclick = function() {
      searchInput.value = '';
      searchInput.focus();
      if (noResults) noResults.style.display = 'none';
    };

    const searchBox = document.getElementById('search-box');
    if (searchBox) {
      searchBox.style.position = 'relative';
      searchBox.appendChild(clearBtn);
    }
  }

  // Monitor search results
  const checkResults = setInterval(function() {
    const results = document.querySelectorAll('.search-result');
    if (searchInput && searchInput.value.length > 0) {
      if (results.length === 0) {
        if (noResults) noResults.style.display = 'block';
      } else {
        if (noResults) noResults.style.display = 'none';
      }
    }
  }, 500);

  // Clear after 10 seconds
  setTimeout(function() {
    clearInterval(checkResults);
  }, 10000);
});
</script>
