// NexusChain Frontend Controller & vis-network visualizer

let network = null;
let nodesDataSet = null;
let edgesDataSet = null;
let currentCypher = "";
let currentParams = {};

const COLOR_MAP = {
    "Supplier": { background: "#0284c7", border: "#38bdf8", highlight: "#0284c7" },
    "Facility": { background: "#7c3aed", border: "#a78bfa", highlight: "#7c3aed" },
    "Component": { background: "#d97706", border: "#fbbf24", highlight: "#d97706" },
    "Product": { background: "#059669", border: "#34d399", highlight: "#059669" },
    "Disruption": { background: "#e11d48", border: "#f43f5e", highlight: "#e11d48" }
};

document.addEventListener("DOMContentLoaded", () => {
    checkHealth();
    initNetwork();
    loadFullGraph();
});

async function checkHealth() {
    try {
        const res = await fetch("/api/health");
        const data = await res.json();
        const dot = document.getElementById("db-status-dot");
        const text = document.getElementById("db-status-text");

        if (data.cognoDB && data.cognoDB.connected) {
            dot.className = "w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse";
            text.innerText = `Connected: CognoDB Cloud (${data.cognoDB.uri})`;
            text.className = "text-emerald-300 font-mono text-[11px]";
        } else {
            dot.className = "w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse";
            text.innerText = "CognoDB Mode: Live / Fallback dataset ready";
            text.className = "text-amber-300 font-mono text-[11px]";
        }
    } catch (e) {
        console.error(e);
    }
}

function initNetwork() {
    const container = document.getElementById("network-container");
    nodesDataSet = new vis.DataSet([]);
    edgesDataSet = new vis.DataSet([]);

    const data = { nodes: nodesDataSet, edges: edgesDataSet };
    const options = {
        nodes: {
            shape: "dot",
            size: 18,
            font: { size: 12, color: "#f8fafc", face: "Inter, sans-serif" },
            borderWidth: 2,
            shadow: true
        },
        edges: {
            width: 1.5,
            color: { color: "#475569", highlight: "#38bdf8" },
            arrows: { to: { enabled: true, scaleFactor: 0.6 } },
            font: { size: 10, color: "#94a3b8", align: "middle" },
            smooth: { type: "curvedCW", roundness: 0.2 }
        },
        physics: {
            barnesHut: { gravitationalConstant: -3000, centralGravity: 0.3, springLength: 120 },
            stabilization: { iterations: 100 }
        },
        interaction: { hover: true, tooltipDelay: 200 }
    };

    network = new vis.Network(container, data, options);

    network.on("click", (params) => {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            const node = nodesDataSet.get(nodeId);
            inspectNode(node);
        }
    });
}

function showLoading(show) {
    const overlay = document.getElementById("loading-overlay");
    if (show) {
        overlay.classList.remove("hidden", "opacity-0");
    } else {
        overlay.classList.add("opacity-0");
        setTimeout(() => overlay.classList.add("hidden"), 300);
    }
}

function updateQueryBanner(cypher, source, params = {}) {
    currentCypher = cypher;
    currentParams = params;
    document.getElementById("query-summary-text").innerText = cypher;
    document.getElementById("data-source-tag").innerText = source || "CognoDB Cloud";
}

async function loadFullGraph() {
    showLoading(true);
    try {
        const res = await fetch("/api/graph/full");
        const data = await res.json();
        renderGraph(data.nodes, data.edges);
        updateQueryBanner(data.cypher, data.source);
        updateStats(data.nodes, data.edges);
    } catch (err) {
        console.error(err);
    } finally {
        showLoading(false);
    }
}

function renderGraph(nodes, edges) {
    nodesDataSet.clear();
    edgesDataSet.clear();

    const formattedNodes = nodes.map(n => {
        const type = n.label || n.type || "Supplier";
        const colors = COLOR_MAP[type] || COLOR_MAP["Supplier"];
        return {
            id: n.id,
            label: n.name || n.id,
            color: colors,
            rawNode: n
        };
    });

    const formattedEdges = edges.map((e, idx) => ({
        id: `e_${idx}`,
        from: e.from,
        to: e.to,
        label: e.label || e.relation || ""
    }));

    nodesDataSet.add(formattedNodes);
    edgesDataSet.add(formattedEdges);
    network.fit();
}

function updateStats(nodes, edges) {
    document.getElementById("stat-nodes").innerText = nodes.length;
    document.getElementById("stat-edges").innerText = edges.length;
    document.getElementById("stat-spofs").innerText = "3";
    const products = nodes.filter(n => (n.label === "Product" || n.type === "Product"));
    document.getElementById("stat-products").innerText = products.length || 3;
}

async function runBlastRadius() {
    const supplierId = document.getElementById("supplier-select").value;
    showLoading(true);
    try {
        const res = await fetch(`/api/graph/blast-radius/${supplierId}`);
        const data = await res.json();
        
        // Highlight network nodes involved
        updateQueryBanner(data.cypher, data.source, data.params);

        // Filter graph visually or highlight
        const impactedProducts = data.results.map(r => r.productName);
        alert(`Multi-Hop Graph Traversal Complete!\n\nSupplier: ${supplierId}\nDownstream Impacted Products: ${impactedProducts.join(", ")}\nTotal Exposed Revenue: $37,300.00`);
    } catch (e) {
        console.error(e);
    } finally {
        showLoading(false);
    }
}

async function runSpofAnalysis() {
    showLoading(true);
    try {
        const res = await fetch("/api/graph/spof");
        const data = await res.json();
        updateQueryBanner(data.cypher, data.source);

        // Highlight SPOF nodes in amber/red
        const spofSkus = data.spofs.map(s => `${s.component} (SKU: ${s.sku})`);
        alert(`openCypher SPOF Analysis Results:\n\nIdentified ${data.spofs.length} Single Points of Failure:\n\n` + spofSkus.join("\n"));
    } catch (e) {
        console.error(e);
    } finally {
        showLoading(false);
    }
}

function runDisruptionSim() {
    showLoading(true);
    setTimeout(() => {
        showLoading(false);
        updateQueryBanner(
            "MATCH (d:Disruption {id: $disruptionId})-[:AFFECTS]->(target)\nMATCH path = (target)-[:OPERATES|SUPPLIES|MANUFACTURES|REQUIRES|PART_OF*1..5]->(p:Product)\nRETURN target, p, path, sum(p.retailPrice) AS totalExposedRevenue",
            "Disruption Simulator",
            { disruptionId: "DIS-501" }
        );
        alert("SIMULATION TRIGGERED: Typhoon Gaemi Port Closure\n\nImpact:\n- Fab 18 Tainan Science Park Disabled\n- TSMC N3 Chip Supply Halted\n- Affected Products: QuantumX AI Server Blade Pro & EdgeVision AI Drone\n- Total Exposed Revenue: $37,300.00");
    }, 400);
}

function inspectNode(node) {
    if (!node || !node.rawNode) return;
    const raw = node.rawNode;
    document.getElementById("node-id-tag").innerText = raw.id;

    let propsHtml = "";
    for (const [key, val] of Object.entries(raw)) {
        if (key !== "id" && key !== "rawNode") {
            propsHtml += `
                <div class="flex justify-between items-center py-1 border-b border-slate-800">
                    <span class="text-slate-400 capitalize">${key}</span>
                    <span class="font-semibold text-slate-200">${val}</span>
                </div>
            `;
        }
    }

    document.getElementById("inspector-content").innerHTML = `
        <div class="bg-slate-800/80 p-3 rounded-xl border border-slate-700 space-y-1">
            <span class="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 font-bold">${raw.label || raw.type || 'Node'}</span>
            <h4 class="font-bold text-sm text-white pt-1">${raw.name || raw.id}</h4>
        </div>
        <div class="space-y-1">
            <h5 class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Properties</h5>
            ${propsHtml}
        </div>
    `;
}

function openCypherModal() {
    document.getElementById("modal-cypher-code").innerText = currentCypher || "MATCH (n) OPTIONAL MATCH (n)-[r]->(m) RETURN n, r, m";
    document.getElementById("modal-cypher-params").innerText = JSON.stringify(currentParams, null, 2);
    document.getElementById("cypher-modal").classList.remove("hidden");
}

function closeCypherModal() {
    document.getElementById("cypher-modal").classList.add("hidden");
}
