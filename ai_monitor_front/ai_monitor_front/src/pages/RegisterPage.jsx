// // pages/RegisterPage.jsx
// import { useState } from "react";
// import { useNavigate, Link } from "react-router-dom";
// import { useAuth } from "../context/AuthContext";
// import AuthLayout from "../components/auth/AuthLayout";
// import {
//   AuthInput, PasswordInput, AuthButton,
//   AuthDivider, ErrorBanner,
// } from "../components/auth/AuthFormParts";

// function StrengthBar({ password }) {
//   const score = (() => {
//     let s = 0;
//     if (password.length >= 8)          s++;
//     if (/[A-Z]/.test(password))        s++;
//     if (/[0-9]/.test(password))        s++;
//     if (/[^A-Za-z0-9]/.test(password)) s++;
//     return s;
//   })();

//   const colors = ["var(--red)", "var(--amber)", "var(--amber)", "var(--teal)", "var(--green)"];
//   const labels = ["", "Weak", "Fair", "Good", "Strong"];

//   if (!password) return null;
//   return (
//     <div style={{ display: "flex", flexDirection: "column", gap: 4, marginTop: -4 }}>
//       <div style={{ display: "flex", gap: 3 }}>
//         {[1, 2, 3, 4].map((i) => (
//           <div key={i} style={{
//             flex: 1, height: 3, borderRadius: 2,
//             background: i <= score ? colors[score] : "var(--bg-overlay)",
//             transition: "background 0.2s",
//           }} />
//         ))}
//       </div>
//       <span style={{
//         fontSize: 10, color: colors[score],
//         fontFamily: "var(--font-ui)", textAlign: "right",
//       }}>
//         {labels[score]}
//       </span>
//     </div>
//   );
// }

// export default function RegisterPage() {
//   const navigate = useNavigate();
//   const { register, loading, error, clearError } = useAuth();

//   const [name,     setName]     = useState("");
//   const [email,    setEmail]    = useState("");
//   const [password, setPassword] = useState("");
//   const [confirm,  setConfirm]  = useState("");
//   const [agreed,   setAgreed]   = useState(false);
//   const [errors,   setErrors]   = useState({});

//   const validate = () => {
//     const e = {};
//     if (!name.trim())                        e.name     = "Name is required";
//     if (!email.trim())                       e.email    = "Email is required";
//     else if (!/\S+@\S+\.\S+/.test(email))    e.email    = "Enter a valid email";
//     if (!password)                           e.password = "Password is required";
//     else if (password.length < 8)            e.password = "Minimum 8 characters";
//     if (confirm !== password)                e.confirm  = "Passwords do not match";
//     if (!agreed)                             e.agreed   = "You must accept the terms";
//     setErrors(e);
//     return Object.keys(e).length === 0;
//   };

//   const handleSubmit = async () => {
//     if (!validate()) return;
//     const ok = await register(name, email, password);
//     if (ok) navigate("/analyzer", { replace: true });
//   };

//   const handleKey = (e) => { if (e.key === "Enter") handleSubmit(); };

//   return (
//     <AuthLayout
//       title="Create account"
//       subtitle="Join the AI coding mentor platform"
//     >
//       <div style={{ display: "flex", flexDirection: "column", gap: 14 }} onKeyDown={handleKey}>
//         <ErrorBanner message={error} onDismiss={clearError} />

//         <AuthInput
//           label="Full Name"
//           type="text"
//           value={name}
//           onChange={(v) => { setName(v); setErrors((e) => ({ ...e, name: null })); }}
//           placeholder="Alex Johnson"
//           autoComplete="name"
//           error={errors.name}
//           icon={
//             <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
//               stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
//               <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
//               <circle cx="12" cy="7" r="4"/>
//             </svg>
//           }
//         />

//         <AuthInput
//           label="Email"
//           type="email"
//           value={email}
//           onChange={(v) => { setEmail(v); setErrors((e) => ({ ...e, email: null })); }}
//           placeholder="you@example.com"
//           autoComplete="email"
//           error={errors.email}
//           icon={
//             <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
//               stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
//               <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
//               <polyline points="22,6 12,13 2,6"/>
//             </svg>
//           }
//         />

//         <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
//           <PasswordInput
//             label="Password"
//             value={password}
//             onChange={(v) => { setPassword(v); setErrors((e) => ({ ...e, password: null })); }}
//             error={errors.password}
//             autoComplete="new-password"
//           />
//           <StrengthBar password={password} />
//         </div>

//         <PasswordInput
//           label="Confirm Password"
//           value={confirm}
//           onChange={(v) => { setConfirm(v); setErrors((e) => ({ ...e, confirm: null })); }}
//           error={errors.confirm}
//           autoComplete="new-password"
//         />

//         {/* Terms checkbox */}
//         <label style={{
//           display: "flex", alignItems: "flex-start", gap: 9, cursor: "pointer",
//         }}>
//           <div
//             onClick={() => { setAgreed((a) => !a); setErrors((e) => ({ ...e, agreed: null })); }}
//             style={{
//               width: 16, height: 16, borderRadius: 4, flexShrink: 0, marginTop: 1,
//               background: agreed ? "var(--accent)" : "var(--bg-surface)",
//               border: `1px solid ${errors.agreed ? "var(--red-border)" : agreed ? "var(--accent)" : "var(--border-default)"}`,
//               display: "flex", alignItems: "center", justifyContent: "center",
//               transition: "all 0.15s",
//             }}
//           >
//             {agreed && (
//               <svg width="10" height="10" viewBox="0 0 24 24" fill="none"
//                 stroke="#fff" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
//                 <polyline points="20,6 9,17 4,12"/>
//               </svg>
//             )}
//           </div>
//           <span style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "var(--font-ui)", lineHeight: 1.5 }}>
//             I agree to the{" "}
//             <span style={{ color: "var(--accent)", cursor: "pointer" }}>Terms of Service</span>
//             {" "}and{" "}
//             <span style={{ color: "var(--accent)", cursor: "pointer" }}>Privacy Policy</span>
//           </span>
//         </label>
//         {errors.agreed && (
//           <span style={{ fontSize: 11, color: "var(--red)", marginTop: -8, fontFamily: "var(--font-ui)" }}>
//             {errors.agreed}
//           </span>
//         )}

//         <AuthButton loading={loading} onClick={handleSubmit}>
//           {loading ? "Creating account…" : "Create Account"}
//         </AuthButton>

//         <p style={{
//           textAlign: "center", fontSize: 12,
//           color: "var(--text-faint)", fontFamily: "var(--font-ui)", margin: 0,
//         }}>
//           Already have an account?{" "}
//           <Link to="/login" style={{ color: "var(--accent)", textDecoration: "none", fontWeight: 600 }}>
//             Sign in
//           </Link>
//         </p>
//       </div>
//     </AuthLayout>
//   );
// }