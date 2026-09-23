import React from 'react';

export default function ToolsTab({ tools, onRefresh }) {
  const defaultTools = [
    {
      name: 'nmap',
      category: 'RECONNAISSANCE',
      risk: 'LOW',
      container: 'kali-sandbox',
      description: 'Network exploration tool and security / port scanner. Supports TCP SYN, UDP, service versioning, and NSE scripts.',
      command_template: 'nmap -sS -sV -Pn <target>',
    },
    {
      name: 'gobuster',
      category: 'ENUMERATION',
      risk: 'LOW',
      container: 'kali-sandbox',
      description: 'Fast URI, DNS subdomain and virtual host brute-forcer written in Go.',
      command_template: 'gobuster dir -u <url> -w /usr/share/wordlists/dirb/common.txt',
    },
    {
      name: 'nikto',
      category: 'VULNERABILITY_SCAN',
      risk: 'LOW',
      container: 'kali-sandbox',
      description: 'Web server vulnerability scanner for dangerous files, outdated server software, and configuration issues.',
      command_template: 'nikto -h <target> -C all',
    },
    {
      name: 'sqlmap',
      category: 'EXPLOITATION',
      risk: 'HIGH',
      container: 'kali-sandbox',
      description: 'Automatic SQL injection and database takeover tool.',
      command_template: 'sqlmap -u "<url>" --batch --dbs',
    },
    {
      name: 'nuclei',
      category: 'VULNERABILITY_SCAN',
      risk: 'MEDIUM',
      container: 'kali-sandbox',
      description: 'Fast and customizable vulnerability scanner based on simple YAML-based DSL templates.',
      command_template: 'nuclei -u <target> -severity critical,high',
    },
    {
      name: 'searchsploit',
      category: 'INTELLIGENCE',
      risk: 'SAFE',
      container: 'kali-sandbox',
      description: 'Command line search tool for Exploit-DB offline repository.',
      command_template: 'searchsploit <service> <version>',
    },
    {
      name: 'metasploit',
      category: 'EXPLOITATION',
      risk: 'CRITICAL',
      container: 'kali-sandbox',
      description: 'Controlled penetration testing framework used for proof-of-concept verification in isolated environment.',
      command_template: 'msfconsole -q -x "<commands>"',
    },
  ];

  const displayTools = tools && tools.length > 0 ? tools : defaultTools;

  return (
    <div>
      <div className="cyber-card">
        <div className="card-header">
          <div className="card-title">
            <span className="prefix">[TOOL]</span> KALI LINUX SANDBOX TOOL INVENTORY
          </div>
          <button className="btn btn-secondary" onClick={onRefresh}>
            REFRESH TOOLS
          </button>
        </div>
        <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 20 }}>
          All tools execute inside the isolated Docker Kali Linux container with strictly bounded privileges and memory quotas.
        </div>

        <div className="table-container">
          <table className="cyber-table">
            <thead>
              <tr>
                <th>TOOL</th>
                <th>CATEGORY</th>
                <th>RISK LEVEL</th>
                <th>ENVIRONMENT</th>
                <th>CAPABILITIES & SYNOPSIS</th>
              </tr>
            </thead>
            <tbody>
              {displayTools.map((t) => {
                const risk = (t.risk || 'LOW').toUpperCase();
                return (
                  <tr key={t.name}>
                    <td>
                      <span className="mono" style={{ fontWeight: 700, color: 'var(--accent-cyan)' }}>
                        {t.name}
                      </span>
                    </td>
                    <td>
                      <span className="badge badge-muted">{t.category || 'UTILITY'}</span>
                    </td>
                    <td>
                      <span className={`badge ${
                        risk === 'CRITICAL' ? 'badge-red' :
                        risk === 'HIGH' ? 'badge-amber' :
                        risk === 'MEDIUM' ? 'badge-muted' : 'badge-green'
                      }`}>
                        {risk}
                      </span>
                    </td>
                    <td>
                      <span className="mono" style={{ fontSize: 11, color: 'var(--text-dim)' }}>
                        {t.container || 'kali-sandbox'}
                      </span>
                    </td>
                    <td>
                      <div style={{ fontSize: 12, color: 'var(--text-main)', marginBottom: 4 }}>
                        {t.description}
                      </div>
                      {t.command_template && (
                        <code style={{ fontSize: 11, color: 'var(--text-dim)' }}>
                          $ {t.command_template}
                        </code>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
