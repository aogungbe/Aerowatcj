document.addEventListener('DOMContentLoaded', function () {
const filtertype = document.getElementById('filter-type');
const filters = document.querySelectorAll('.filter-option');

function cleardatalist(datalist) {
  while (datalist.hasChildNodes()) {
    datalist.removeChild(datalist.firstChild);
  }
}
// Add click event listener to each card
filters.forEach(filter => {
    filter.addEventListener('click', () => {
      console.log("clicked",filter)
        // Remove 'active'class and change colour  from all cards(SETTINGS FOR INACTIVE CARDS)
        filters.forEach(f => {
        f.classList.remove('active', 'text-white'); 
        f.style.backgroundColor = '#ffffff';
        filter.classList.add('text-black');
        });
        // Add 'active' class to the clicked card
        filter.classList.add('active', 'text-white');
        // Ensure background color change is visible
        filter.style.backgroundColor = '#002d72';
        // Pass filtertype to python
        filtertype.value = filter.id; 
        console.log("this is the filtertype",filtertype);
    if (filter.id == "destination"|| filter.id == "arrival") {
      const search = document.getElementById('form1');
      search.type = "text";
      const old = document.getElementById('routeform1');
      old.type = "hidden";
      const old2 = document.getElementById('routeform2');
      old2.type = "hidden";
    fetch('https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat')
      .then(response => response.text())
      .then(data => {
        const airports = data.split('\n').map(line => line.split(','));
        const airportList = airports.map(airport => {
          if (airport.length > 5) {
            return {
              name: airport[1].replace(/"/g, ''),
              icao: airport[5].replace(/"/g, ''),
              country :airport[3].replace(/"/g, ''),
              city: airport[2].replace(/"/g, '')
            };
          } else {
            return null;
          }
        }).filter(airport => airport !== null);
            const datalist = document.getElementById('autocomplete-options');
            cleardatalist(datalist);
            airportList.forEach(airport => {
              if (airport.name && airport.icao) {
                const option = document.createElement('option');
                option.value = `${airport.name} (${airport.icao}),(${airport.city},${airport.country})`;
                datalist.appendChild(option);
              }
            });
          })
          .catch(error => console.error('Error:', error)); 
        const form = document.getElementById('search-form');    
        // Add event listener for form submission
        form.addEventListener('submit', function (event) {
            event.preventDefault(); // Prevent the form from submitting normally    
            // Get the value of the input field
            let inputvalue = filtertype.value; // Ensure to trim any extra whitespace
            if (inputvalue) {
              console.log("this is the inputvalue",inputvalue);
            } else {
              inputvalue = "destination";
            } 
            const airport = document.getElementById('form1');
            const airportvalue = airport.value.split(/[(,)]/);
            // Assuming the ICAO code is the second value in the comma-separated list
            if (airportvalue[1]) {
              airport_icao = airportvalue[1].trim();
          } else {
              airport_icao = '';
          }
            console.log("this is the icao",airport_icao)
            // Construct the URL dynamically
            const url = `${searchBaseUrl}${encodeURIComponent(inputvalue)}/${encodeURIComponent(airport_icao)}`;
            // Set the form action to the constructed URL
            form.action = url;
            // Submit the form
            form.submit();           
        });
      } else {
        const routesearch = document.querySelectorAll('.routeform');
        routesearch.forEach(search_bar => {
          search_bar.type = "text"
          const old = document.getElementById('form1');
          old.type = "hidden";
        })
        fetch('https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat')
      .then(response => response.text())
      .then(data => {
        const airports = data.split('\n').map(line => line.split(','));
        const airportList = airports.map(airport => {
          if (airport.length > 5) {
            return {
              name: airport[1].replace(/"/g, ''),
              icao: airport[5].replace(/"/g, ''),
              country :airport[3].replace(/"/g, ''),
              city: airport[2].replace(/"/g, '')
            };
          } else {
            return null;
          }
        }).filter(airport => airport !== null);
            const datalist = document.getElementById('autocomplete-options');
            cleardatalist(datalist);
            airportList.forEach(airport => {
              if (airport.name && airport.icao) {
                const option = document.createElement('option');
                option.value = `${airport.name} (${airport.icao}),(${airport.city},${airport.country})`;
                datalist.appendChild(option);
              }
            });
          })
          .catch(error => console.error('Error:', error)); 
        const form = document.getElementById('search-form');
        form.addEventListener('submit', function (event) {
          event.preventDefault(); // Prevent the form from submitting normally    
          // Get the value of the input field
          let inputvalue = filtertype.value; // Ensure to trim any extra whitespace
          if (inputvalue) {
            console.log("this is the inputvalue",inputvalue);
          } else {
            inputvalue = "destination";
          } 
          const airport1 = document.getElementById('routeform1');
          const airport1value = airport1.value.split(/[(,)]/);
          const airport2 = document.getElementById('routeform2');
          const airport2value = airport2.value.split(/[(,)]/);
          // Assuming the ICAO code is the second value in the comma-separated list
          if (airport1value[1]) {
            airport_icao1 = airport1value[1].trim();
        } else {
            airport_icao1 = '';
        }
        // Assuming the ICAO code is the second value in the comma-separated list
        if (airport2value[1]) {
          airport_icao2 = airport2value[1].trim();
      } else {
          airport_icao2 = '';
      }
          console.log("this is the icao 1",airport_icao1)
          console.log("this is the icao 2",airport_icao2)
          // Construct the URL dynamically
          const url = `${routebaseurl}${encodeURIComponent(airport_icao1)}/${encodeURIComponent(airport_icao2)}`;
          // Set the form action to the constructed URL
          form.action = url;
          // Submit the form
          form.submit();           
      });
      }
    })
    });
  });

