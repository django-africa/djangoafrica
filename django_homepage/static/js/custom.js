$(".product-item").isotope({
  itemSelector: ".item",
  layoutMode: "fitRows"
});
$(".product-menu ul li").click(function() {
  console.log("iiiii");
  $(".product-menu ul li").removeClass("active");
  $(this).addClass("active");

  var selector = $(this).attr("data-filter");
  console.log(selector);
  $(".product-item").isotope({
    filter: selector
  });
  return false;
});

$(".main_menu_wrap").singlePageNav({
  offset: $(".single-page-nav").outerHeight(),
  threshold: 120,
  speed: 400,
  currentClass: "current",
  easing: "swing",
  filter: ":not(.external)",

  beforeStart: function() {
    console.log("begin scrolling");
  },
  onComplete: function() {
    console.log("done scrolling");
  }
});

$(".sidebar-toggle").on("click", function() {
  $(".fixed-sidebar").addClass("open");
  console.log("test1");
});
$(".sidebar-close").on("click", function() {
  $(".fixed-sidebar").removeClass("open");
  console.log("test2");
});

$(".project1-item").isotope({
  itemSelector: ".item",
  layoutMode: "fitRows"
});
$(".project1-menu ul li").click(function() {
  console.log("iiiii");
  $(".project1-menu ul li").removeClass("active");
  $(this).addClass("active");

  var selector = $(this).attr("data-filter");
  console.log(selector);
  $(".project1-item").isotope({
    filter: selector
  });
  return false;
});
