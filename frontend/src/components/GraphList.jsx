import React from "react";

const GraphList = ({ graphs, onGraphSelect, selectedGraphId }) => {
    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleString();
    };

    const getGraphStatus = (graph) => {
        const nodeCount = graph.nodes.length;
        const edgeCount = graph.edges.length;

        if (nodeCount === 0) return "empty";
        if (nodeCount <= 5) return "small";
        if (nodeCount <= 15) return "medium";
        return "large";
    };

    const getStatusColor = (status) => {
        switch (status) {
            case "empty":
                return "#95a5a6";
            case "small":
                return "#2ecc71";
            case "medium":
                return "#f39c12";
            case "large":
                return "#e74c3c";
            default:
                return "#95a5a6";
        }
    };

    const getStatusText = (status) => {
        switch (status) {
            case "empty":
                return "Empty";
            case "small":
                return "Small";
            case "medium":
                return "Medium";
            case "large":
                return "Large";
            default:
                return "Unknown";
        }
    };

    const handleDeleteGraph = async (graphId, e) => {
        e.stopPropagation(); // Prevent triggering onGraphSelect
        try {
            const response = await fetch(`http://localhost:8080/batch?group_id=${encodeURIComponent(graphId)}`, {
                method: 'DELETE',
            });
            if (response.ok) {
                // Remove the graph from the list
                if (typeof window !== 'undefined' && window.toast) {
                    window.toast.success('Batch deleted successfully');
                }
                if (typeof window !== 'undefined' && window.dispatchEvent) {
                    window.dispatchEvent(new CustomEvent('batchDeleted', { detail: { graphId } }));
                }
            } else {
                if (typeof window !== 'undefined' && window.toast) {
                    window.toast.error('Failed to delete batch');
                }
            }
        } catch (err) {
            if (typeof window !== 'undefined' && window.toast) {
                window.toast.error('Error deleting batch');
            }
        }
    };

    return (
        <div className="graph-list">
            <div className="graph-list-header">
                <h2>Available Graphs ({Object.keys(graphs).length})</h2>
                <p>Click on a graph to view its details</p>
            </div>

            {Object.keys(graphs).length === 0 ? (
                <div className="no-graphs">
                    <p>No graphs available. Waiting for WebSocket messages...</p>
                    <div className="loading-spinner"></div>
                    <p className="test-hint">
                        Use the test controls above to create sample graphs and test the
                        functionality.
                    </p>
                </div>
            ) : (
                <div className="graphs-grid">
                    {Object.entries(graphs).map(([graphId, graph]) => {
                        const status = getGraphStatus(graph);
                        const rootNode = graph.nodes.find((node) => node.data.isRoot);
                        // alert(JSON.stringify(rootNode));

                        return (
                            <div
                                key={graphId}
                                className={`graph-card ${selectedGraphId === graphId ? "selected" : ""}`}
                                onClick={() => onGraphSelect(graphId)}
                            >
                                <div className="graph-card-header">
                                    <h3>{graphId}</h3>
                                    <span
                                        className="status-badge"
                                        style={{ backgroundColor: getStatusColor(status) }}
                                    >
                                        {getStatusText(status)}
                                    </span>
                                </div>

                                <div className="graph-card-stats">
                                    <div className="stat-item">
                                        <span className="stat-label">Alerts:</span>
                                        <span className="stat-value">{graph.nodes.length}</span>
                                    </div>
                                    <div className="stat-item">
                                        <span className="stat-label">Edges:</span>
                                        <span className="stat-value">{graph.edges.length}</span>
                                    </div>
                                    <div className="stat-item">
                                        <span className="stat-label">Created:</span>
                                        <span className="stat-value">
                                            {formatDate(graph.createdAt)}
                                        </span>
                                    </div>
                                </div>

                                {rootNode && (
                                    <div className="root-info">
                                        <span className="root-label">Root:</span>
                                        <span className="root-value">{rootNode.data.label}</span>
                                    </div>
                                )}

                                <div className="graph-card-footer">
                                    <button className="view-btn">View Graph</button>
                                    <button
                                        className="delete-btn"
                                        onClick={(e) => handleDeleteGraph(graphId, e)}
                                        style={{ marginLeft: '0.5rem', background: '#dc2626', color: 'white', border: 'none', borderRadius: '6px', padding: '0.375rem 0.75rem', fontSize: '0.7rem', cursor: 'pointer' }}
                                    >
                                        Delete
                                    </button>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
};

export default GraphList;
