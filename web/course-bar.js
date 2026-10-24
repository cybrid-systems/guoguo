/* Fill #course-bar from /catalog.json. The page sets data-course to its id. */
(function () {
  var bar = document.getElementById("course-bar");
  if (!bar) return;
  var here = bar.getAttribute("data-course") || "";
  fetch("/catalog.json")
    .then(function (res) {
      if (!res.ok) throw new Error("catalog");
      return res.json();
    })
    .then(function (data) {
      var courses = data && data.courses;
      if (!courses || !courses.length) return;
      bar.replaceChildren();
      courses.forEach(function (course) {
        var open = course.status === "open" && course.href;
        var el = document.createElement(open ? "a" : "span");
        el.textContent = course.title + (open ? "" : " · 还没开");
        if (open) {
          el.href = course.href;
          if (course.id === here) el.setAttribute("aria-current", "page");
        } else {
          el.className = "soon";
        }
        bar.append(el);
      });
    })
    .catch(function () {});
})();
