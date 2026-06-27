// /* @odoo-module */

// import { Component, useState, onWillStart } from "@odoo/owl";
// import { registry } from "@web/core/registry";
// import { useService } from "@web/core/utils/hooks";

// export class StartStopMenu extends Component {
//     static template = "concept_project_manpower_indicator.StartStopButton";

//     setup() {
//         this.state = useState({
//             isStarted: false,
//             showButton: false, // Controls visibility based on department
//         });
//         this.rpc = useService("rpc");
//         this.notification = useService("notification"); // To show errors

//         // Fetch initial status when component is about to start
//         onWillStart(async () => {
//             await this.fetchInitialStatus();
//         });
//     }

//     /**
//      * Fetch the user's initial status from the server.
//      */
//     async fetchInitialStatus() {
//         try {
//             const result = await this.rpc("/project_manpower/get_status", {});
//             this.state.isStarted = result.is_started;
//             // this.state.showButton = result.is_sales_member;
//         } catch (e) {
//             console.error("Failed to fetch manpower status:", e);
//             this.state.showButton = false; // Hide button on error
//         }
//     }

  

//     /**
//      * Handle the click event to start or stop work.
//      */
//     async toggleWork() {
//         // Optimistically toggle state
//         const targetState = !this.state.isStarted;
//         this.state.isStarted = targetState;

//         let rpcCall;
//         if (targetState) { // If target is to be "started"
//             rpcCall = this.rpc("/project_manpower/start_work", {});
//         } else { // If target is to be "stopped"
//             rpcCall = this.rpc("/project_manpower/stop_work", {});
//         }

//         try {
//             const result = await rpcCall;
//             // Handle controlled errors from the server
//             if (result.status === 'error') {
//                 this.state.isStarted = !targetState; // Revert state
//                 this.notification.add(result.message, { type: 'danger' });
//             }
//             // On success, the optimistic state was correct.
//         } catch (e) {
//             // Revert state on unexpected RPC failure
//             this.state.isStarted = !targetState;
//             this.notification.add("Failed to update status. Please try again.", { type: 'danger' });
//             console.error("Failed to toggle work:", e);
//         }
//     }
// }

// export const systrayStartStop = {
//     Component: StartStopMenu,
// };

// registry.category("systray").add("concept_project_manpower_indicator.start_stop_button", systrayStartStop, { sequence: 102 });


/* @odoo-module */
/* @odoo-module */
import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class StartStopMenu extends Component {
    static template = "concept_project_manpower_indicator.StartStopButton";

    setup() {
        this.state = useState({
            isStarted: false,
            allUsers: [],
            activeTab: 'on_duty',
        });
        this.rpc = useService("rpc");

        onWillStart(async () => {
            await this.fetchStatusData();
        });
    }

    async fetchStatusData() {
        try {
            const statusResult = await this.rpc("/project_manpower/get_status", {});
            this.state.isStarted = statusResult.is_started;

            this.state.allUsers = await this.rpc("/project_manpower/get_all_users_status", {});
        } catch (e) {
            console.error("Failed to populate user list:", e);
        }
    }

    get displayedUsers() {
        if (this.state.activeTab === 'on_duty') {
            return this.state.allUsers.filter(u => u.is_started === true);
        } else {
            return this.state.allUsers.filter(u => u.is_started === false);
        }
    }

    // UPDATED: Now stops the dropdown from closing when you click a tab
    setTab(tabName, ev) {
        if (ev) {
            ev.stopPropagation(); // This prevents Bootstrap from closing the menu
        }
        this.state.activeTab = tabName;
    }

    async toggleWork(targetState) {
        if (this.state.isStarted === targetState) return;
        
        let rpcPath = targetState ? "/project_manpower/start_work" : "/project_manpower/stop_work";
        try {
            const result = await this.rpc(rpcPath, {});
            if (result.status !== 'error') {
                this.state.isStarted = targetState;
                await this.fetchStatusData(); 
            }
        } catch (e) {
            console.error("Update failed:", e);
        }
    }
}

registry.category("systray").add("concept_project_manpower_indicator.start_stop_button", {
    Component: StartStopMenu,
}, { sequence: 102 });