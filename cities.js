/* Location Potential Europe - live city sections. Regenerate: python3 work/make_cities_js.py */
window.LPE_BASE=(function(){var m=location.pathname.match(/^(.*\/location-potential-europe\/)/);return m?m[1]:"/";})();
window.CITIES=[
 {id:"hub",name:"All cities",url:""},
 {id:"uk-london",name:"London",url:"london/"},
 {id:"uk-manchester",name:"Manchester",url:"manchester/"},
 {id:"uk-birmingham",name:"Birmingham",url:"birmingham/"},
 {id:"uk-leeds",name:"Leeds",url:"leeds/"},
 {id:"uk-bristol",name:"Bristol",url:"bristol/"},
 {id:"uk-liverpool",name:"Liverpool",url:"liverpool/"},
 {id:"uk-sheffield",name:"Sheffield",url:"sheffield/"},
 {id:"uk-glasgow",name:"Glasgow",url:"glasgow/"},
 {id:"uk-edinburgh",name:"Edinburgh",url:"edinburgh/"},
 {id:"paris",name:"Paris",url:"paris/"},
 {id:"madrid",name:"Madrid",url:"madrid/"},
 {id:"barcelona",name:"Barcelona",url:"barcelona/"},
 {id:"berlin",name:"Berlin",url:"berlin/"},
 {id:"munich",name:"Munich",url:"munich/"},
 {id:"milan",name:"Milan",url:"milan/"},
 {id:"rome",name:"Rome",url:"rome/"},
 {id:"amsterdam",name:"Amsterdam",url:"amsterdam/"},
 {id:"vienna",name:"Vienna",url:"vienna/"},
 {id:"brussels",name:"Brussels",url:"brussels/"},
 {id:"hamburg",name:"Hamburg",url:"hamburg/"},
 {id:"prague",name:"Prague",url:"prague/"},
 {id:"warsaw",name:"Warsaw",url:"warsaw/"},
 {id:"lisbon",name:"Lisbon",url:"lisbon/"},
 {id:"stockholm",name:"Stockholm",url:"stockholm/"},
 {id:"copenhagen",name:"Copenhagen",url:"copenhagen/"},
 {id:"dublin",name:"Dublin",url:"dublin/"}
];
(function(){
 const base=window.LPE_BASE, path=location.pathname;
 const cur=(window.CITIES.find(c=>c.url&&path.indexOf(base+c.url)===0)||window.CITIES[0]).id;
 const nav=document.getElementById("citynav");
 if(nav){
  nav.innerHTML='<span class="cn-label cn-full">Best area in the city of:</span><span class="cn-label cn-short">Area:</span>'+window.CITIES.map(c=>
   `<a href="${base+c.url}"${c.id===cur?' class="on"':''}>${c.name}</a>`).join("");
 }
})();
