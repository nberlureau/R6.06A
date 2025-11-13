// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::sync::{Arc, Mutex};
use tauri::Manager;
use tauri_plugin_shell::process::CommandChild;
use tauri_plugin_shell::ShellExt;

struct AppState {
    backend_process: Arc<Mutex<Option<CommandChild>>>,
    // ollama_process: Arc<Mutex<Option<Child>>>,
}

#[tauri::command]
async fn start_services(app_handle: tauri::AppHandle) -> Result<(), String> {
    // let resource_dir = app_handle.path().resource_dir().unwrap();

    // // Start Ollama
    // let ollama_path = get_ollama_path(&resource_dir);
    // #[cfg(not(windows))]
    // std::fs::set_permissions(&ollama_path, std::os::unix::fs::PermissionsExt::from_mode(0o755))
    //   .map_err(|e| format!("Permission error: {}", e))?;

    // let mut ollama_cmd = Command::new(ollama_path)
    //   .stdout(Stdio::null())
    //   .stderr(Stdio::null())
    //   .spawn()
    //   .map_err(|e| format!("Ollama start failed: {}", e))?;

    // Start Python backend
    let backend_command = app_handle.shell().sidecar("backend").unwrap();
    let (_, backend) = backend_command.spawn().expect("Failed to spawn backend");

    let state = app_handle.state::<AppState>();
    // *state.ollama_process.lock().unwrap() = Some(ollama_cmd);
    *state.backend_process.lock().unwrap() = Some(backend);

    Ok(())
}

// fn get_ollama_path(resource_dir: &PathBuf) -> PathBuf {
//     #[cfg(target_os = "windows")]
//     return resource_dir.join("bin/windows/ollama.exe");

//     #[cfg(target_os = "linux")]
//     return resource_dir.join("bin/linux/ollama");
// }

fn main() {
    let context = tauri::generate_context!();

    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .manage(AppState {
            // ollama_process: Arc::new(Mutex::new(None)),
            backend_process: Arc::new(Mutex::new(None)),
        })
        .setup(|app| {
            let app_handle = app.handle().clone();
            tauri::async_runtime::spawn(async move {
                if let Err(e) = start_services(app_handle).await {
                    eprintln!("Service startup failed: {}", e);
                    #[cfg(debug_assertions)]
                    panic!("Startup failed: {}", e);
                }
            });
            Ok(())
        })
        .build(context)
        .expect("error while building tauri application")
        .run(|app, event| {
            if let tauri::RunEvent::Exit = event {
                let state = app.state::<AppState>();
                // if let Some(mut child) = state.ollama_process.lock().unwrap().take() {
                //     let _ = child.kill();
                // }
                if let Some(child) = state.backend_process.lock().unwrap().take() {
                    let _ = child.kill();
                };
            }
        });
}

// fn main() {
//     app_lib::run();
// }
