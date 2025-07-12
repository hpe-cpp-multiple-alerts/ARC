import React, { useState } from 'react';

const redAccent = '#dc2626';

const FeedbackPage = ({ graphId, graph, onClose }) => {
    // Extract alerts and edges from the graph
    const alerts = graph ? graph.nodes.map(n => ({
        id: n.data.id,
        label: n.data.label,
        service: n.data.properties?.service,
        summary: n.data.properties?.summary,
        parent_id: n.data.parentId,
    })) : [];
    const edges = graph ? graph.edges.map(e => ({
        id: `${e.data.source}->${e.data.target}`,
        source: e.data.source,
        target: e.data.target,
    })) : [];

    // 1. Service group membership (multi-select)
    const [notBelongIds, setNotBelongIds] = useState([]);
    // 2. Link correctness (multi-select)
    const [falsePositiveIds, setFalsePositiveIds] = useState([]);
    // 3. New links
    const [newLinkSource, setNewLinkSource] = useState(alerts[0]?.id || '');
    const [newLinkTarget, setNewLinkTarget] = useState(alerts[1]?.id || '');
    const [addedLinks, setAddedLinks] = useState([]);

    const handleNotBelongChange = (id) => {
        setNotBelongIds((prev) =>
            prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
        );
    };
    const handleFalsePositiveChange = (id) => {
        setFalsePositiveIds((prev) =>
            prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
        );
    };
    const handleAddLink = () => {
        if (!newLinkSource || !newLinkTarget) return;
        if (newLinkSource === newLinkTarget) return;
        // Prevent duplicate links
        if (addedLinks.some(l => l.source === newLinkSource && l.target === newLinkTarget)) return;
        setAddedLinks((prev) => [
            ...prev,
            { source: newLinkSource, target: newLinkTarget }
        ]);
    };
    const handleSubmit = async (e) => {
        e.preventDefault();
        const feedback = {
            graphId,
            notBelong: notBelongIds,
            falsePositives: falsePositiveIds.map(id => {
                const [source, target] = id.split('->');
                return { source, target };
            }),
            addedLinks,
        };
        try {
            console.log('Feedback submitted:', feedback);
            const response = await fetch('http://localhost:8080/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(feedback),
            });
            if (response.ok) {
                alert('Feedback submitted!');
                if (onClose) onClose();
            } else {
                alert('Failed to submit feedback.');
            }
        } catch (err) {
            alert('Error submitting feedback.');
        }
    };
    if (!graph) {
        return (
            <div style={{ maxWidth: 500, margin: '2rem auto', color: redAccent, textAlign: 'center' }}>
                No data found for this group.
                {onClose && (
                    <><br /><button
                        style={{
                            marginTop: '1.5rem',
                            background: '#3b82f6',
                            color: '#fff',
                            border: 'none',
                            borderRadius: 8,
                            padding: '0.6rem 1.2rem',
                            fontSize: '1rem',
                            cursor: 'pointer',
                            fontWeight: 500,
                            boxShadow: '0 1px 4px rgba(59,130,246,0.08)'
                        }}
                        onClick={onClose}
                    >
                        Close
                    </button></>
                )}
            </div>
        );
    }
    return (
        <div style={{ maxWidth: "50vw", margin: '.75rem auto', background: '#fff', border: '1.5px solid #e2e8f0', borderRadius: 18, padding: '1.5rem 2.2rem', boxShadow: '0 4px 32px rgba(59,130,246,0.07)' }}>
            <div style={{ marginBottom: '1.2rem', textAlign: 'center' }}>
                <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#3b82f6', letterSpacing: 0.5 }}>Feedback for Group</div>
                <div style={{ fontSize: '0.98rem', color: '#1e293b', marginTop: 4, wordBreak: 'break-all', opacity: 0.8 }}>{graphId}</div>
            </div>
            <form onSubmit={handleSubmit}>
                {/* 1. Service group membership */}
                <div style={{ marginBottom: '2rem', paddingBottom: '1rem', borderBottom: '1px solid #e2e8f0' }}>
                    <div style={{ fontSize: '0.97rem', color: '#1e293b', marginBottom: 8, fontWeight: 500 }}>Alerts that <span style={{ color: redAccent }}>do NOT belong</span> to this group:</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12 }}>
                        {alerts.map(alert => (
                            <label key={alert.id} style={{ display: 'flex', alignItems: 'center', background: notBelongIds.includes(alert.id) ? '#fef2f2' : '#f8fafc', border: `1px solid ${notBelongIds.includes(alert.id) ? redAccent : '#e2e8f0'}`, borderRadius: 6, padding: '6px 12px', fontSize: '0.85rem', color: '#1e293b', cursor: 'pointer', transition: 'background 0.2s' }}>
                                <input
                                    type="checkbox"
                                    checked={notBelongIds.includes(alert.id)}
                                    onChange={() => handleNotBelongChange(alert.id)}
                                    style={{ accentColor: redAccent, marginRight: 8 }}
                                />
                                <span>{alert.label} <span style={{ color: '#64748b', fontSize: '0.8em' }}>({alert.service})</span></span>
                            </label>
                        ))}
                    </div>
                </div>
                {/* 2. Link correctness */}
                <div style={{ marginBottom: '2rem', paddingBottom: '1rem', borderBottom: '1px solid #e2e8f0' }}>
                    <div style={{ fontSize: '0.97rem', color: '#1e293b', marginBottom: 8, fontWeight: 500 }}>Links that are <span style={{ color: redAccent }}>false positives</span>:</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12 }}>
                        {edges.map(edge => (
                            <label key={edge.id} style={{ display: 'flex', alignItems: 'center', background: falsePositiveIds.includes(edge.id) ? '#fef2f2' : '#f8fafc', border: `1px solid ${falsePositiveIds.includes(edge.id) ? redAccent : '#e2e8f0'}`, borderRadius: 6, padding: '6px 12px', fontSize: '0.85rem', color: '#1e293b', cursor: 'pointer', transition: 'background 0.2s' }}>
                                <input
                                    type="checkbox"
                                    checked={falsePositiveIds.includes(edge.id)}
                                    onChange={() => handleFalsePositiveChange(edge.id)}
                                    style={{ accentColor: redAccent, marginRight: 8 }}
                                />
                                <span>{edge.source} → {edge.target}</span>
                            </label>
                        ))}
                    </div>
                </div>
                {/* 3. New links */}
                <div style={{ marginBottom: '2rem' }}>
                    <div style={{ fontSize: '0.97rem', color: '#1e293b', marginBottom: 8, fontWeight: 500 }}>Add new link:</div>
                    <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
                        <select value={newLinkSource} onChange={e => setNewLinkSource(e.target.value)} style={{ fontSize: '0.85rem', padding: 4, borderRadius: 4, border: '1px solid #e2e8f0' }}>
                            {alerts.map(alert => (
                                <option key={alert.id} value={alert.id}>{alert.label}</option>
                            ))}
                        </select>
                        <span style={{ fontSize: '0.85rem' }}>→</span>
                        <select value={newLinkTarget} onChange={e => setNewLinkTarget(e.target.value)} style={{ fontSize: '0.85rem', padding: 4, borderRadius: 4, border: '1px solid #e2e8f0' }}>
                            {alerts.filter(a => a.id !== newLinkSource).map(alert => (
                                <option key={alert.id} value={alert.id}>{alert.label}</option>
                            ))}
                        </select>
                        <button type="button" onClick={handleAddLink} style={{ fontSize: '0.85rem', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: 4, padding: '4px 14px', cursor: 'pointer', fontWeight: 500 }}>Add</button>
                    </div>
                    {addedLinks.length > 0 && (
                        <div style={{ fontSize: '0.85rem', color: '#475569', marginTop: 4 }}>
                            <b>Added Links:</b>
                            <ul style={{ margin: 0, paddingLeft: 16 }}>
                                {addedLinks.map((l, i) => (
                                    <li key={i}>{l.source} → {l.target}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
                <button type="submit" style={{ background: '#10b981', color: '#fff', border: 'none', borderRadius: 8, padding: '0.7rem 1.25rem', fontSize: '1rem', cursor: 'pointer', width: '100%', fontWeight: 500, boxShadow: '0 1px 4px rgba(16,185,129,0.08)' }}>
                    Submit Feedback
                </button>
            </form>
        </div>
    );
};

export default FeedbackPage; 