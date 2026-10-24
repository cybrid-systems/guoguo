/* Render the course list into #catalog. */
(function () {
  var host = document.getElementById("catalog");
  if (!host) return;
  fetch("/catalog.json")
    .then(function (res) {
      if (!res.ok) throw new Error("catalog");
      return res.json();
    })
    .then(function (data) {
      var courses = data && data.courses;
      host.replaceChildren();
      if (!courses || !courses.length) {
        host.textContent = "名册是空的。";
        return;
      }
      courses.forEach(function (course) {
        var card = document.createElement("article");
        var title = document.createElement("h2");
        title.textContent = course.title;
        var summary = document.createElement("p");
        summary.textContent = course.summary || "";
        card.append(title, summary);
        if (course.status === "open" && course.href) {
          var link = document.createElement("a");
          link.href = course.href;
          link.textContent = "打开";
          card.append(link);
        } else {
          var later = document.createElement("p");
          later.className = "muted";
          later.textContent = "还没开";
          card.append(later);
        }
        host.append(card);
      });
    })
    .catch(function () {
      host.textContent = "名册没有读到。用 make run 打开后再刷新。";
    });
})();
