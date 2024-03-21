function createParallelChart(data) {
  const width = 928;
  const height = 720;

  const sankey = d3
    .sankey()
    .nodeSort(null)
    .linkSort(null)
    .nodeWidth(4)
    .nodePadding(20)
    .extent([
      [0, 5],
      [width, height - 5],
    ]);

  const color = d3.scaleOrdinal(["#f19d38", "#333f99", "#f19d38", "#333f99"]);
  const svg = d3
    .create("svg")
    .attr("viewBox", [0, 0, width, height])
    .attr("width", width)
    .attr("height", height)
    .attr("style", "max-width: 100%; height: auto;");

  const { nodes, links } = sankey({
    nodes: data.nodes.map((d) => Object.create(d)),
    links: data.links.map((d) => Object.create(d)),
  });

  svg
    .append("g")
    .selectAll("rect")
    .data(nodes)
    .join("rect")
    .attr("x", (d) => d.x0)
    .attr("y", (d) => d.y0)
    .attr("height", (d) => d.y1 - d.y0)
    .attr("width", (d) => d.x1 - d.x0)
    .append("title")
    .text((d) => `${d.name}\n${d.value.toLocaleString()}`);

  svg
    .append("g")
    .attr("fill", "none")
    .selectAll("g")
    .data(links)
    .join("path")
    .attr("d", d3.sankeyLinkHorizontal())
    .attr("stroke", (d) => color(d.names[0]))
    .attr("stroke-width", (d) => d.width)
    .style("mix-blend-mode", "multiply")
    .append("title")
    .text((d) => `${d.names.join(" → ")}\n${d.value.toLocaleString()}`);

  svg
    .append("g")
    .style("font", "10px sans-serif")
    .selectAll("text")
    .data(nodes)
    .join("text")
    .attr("x", (d) => (d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6))
    .attr("y", (d) => (d.y1 + d.y0) / 2)
    .attr("dy", "0.35em")
    .attr("text-anchor", (d) => (d.x0 < width / 2 ? "start" : "end"))
    .text((d) => d.name)
    .append("tspan")
    .attr("fill-opacity", 0.7)
    .text((d) => ` ${d.value.toLocaleString()}`);

  return svg.node();
}

function createBarChart(data) {
  const width = 928;
  const height = 500;
  const marginTop = 30;
  const marginRight = 0;
  const marginBottom = 30;
  const marginLeft = 40;

  // Declare the x (horizontal position) scale.
  const x = d3
    .scaleBand()
    .domain(
      d3.groupSort(
        data,
        ([d]) => -d.frequency,
        (d) => d.letter
      )
    ) // descending frequency
    .range([marginLeft, width - marginRight])
    .padding(0.1);

  // Declare the y (vertical position) scale.
  const y = d3
    .scaleLinear()
    .domain([0, d3.max(data, (d) => d.frequency)])
    .range([height - marginBottom, marginTop]);

  // Create the SVG container.
  const svg = d3
    .create("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [0, 0, width, height])
    .attr("style", "max-width: 100%; height: auto;");

  // Add a rect for each bar.
  svg
    .append("g")
    .attr("fill", "steelblue")
    .selectAll()
    .data(data)
    .join("rect")
    .attr("x", (d) => x(d.letter))
    .attr("y", (d) => y(d.frequency))
    .attr("height", (d) => y(0) - y(d.frequency))
    .attr("width", x.bandwidth());

  // Add the x-axis and label.
  svg
    .append("g")
    .attr("transform", `translate(0,${height - marginBottom})`)
    .call(d3.axisBottom(x).tickSizeOuter(0));

  // Add the y-axis and label, and remove the domain line.
  svg
    .append("g")
    .attr("transform", `translate(${marginLeft},0)`)
    .call(d3.axisLeft(y).tickFormat((y) => (y * 100).toFixed()))
    .call((g) => g.select(".domain").remove())
    .call((g) =>
      g
        .append("text")
        .attr("x", -marginLeft)
        .attr("y", 10)
        .attr("fill", "currentColor")
        .attr("text-anchor", "start")
        .text("↑ Frequency (%)")
    );

  // Return the SVG element.
  return svg.node();
}
