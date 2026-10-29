import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    width: 1280
    height: 720
    property string errorMessage: ""
    function signIn() {
        errorMessage = ""
        sddm.login(username.text, password.text, sessionBox.currentIndex)
    }
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#080715" }
            GradientStop { position: 0.5; color: "#24123f" }
            GradientStop { position: 1.0; color: "#070811" }
        }
    }
    Rectangle {
        id: halo
        width: Math.min(root.width * 0.57, 720)
        height: width
        radius: width / 2
        anchors.centerIn: parent
        color: "transparent"
        border.width: 10
        border.color: "#9a63ea"
        opacity: 0.3
        SequentialAnimation on opacity {
            loops: Animation.Infinite
            NumberAnimation { to: 0.12; duration: 2500; easing.type: Easing.InOutSine }
            NumberAnimation { to: 0.4; duration: 2500; easing.type: Easing.InOutSine }
        }
    }
    Rectangle {
        width: halo.width * 0.75
        height: width
        radius: width / 2
        anchors.centerIn: halo
        color: "#171027"
        border.color: "#603b98"
        border.width: 2
    }
    ColumnLayout {
        width: Math.min(root.width - 40, 480)
        anchors.centerIn: parent
        spacing: 16
        Text {
            Layout.alignment: Qt.AlignHCenter
            text: "AEVONYR"
            color: "#fff4ff"
            font.pixelSize: 46
            font.bold: true
            font.letterSpacing: 7
        }
        Text {
            Layout.alignment: Qt.AlignHCenter
            text: "ONE SYSTEM. TWO WORLDS."
            color: "#c8a9ec"
            font.pixelSize: 12
            font.letterSpacing: 3
        }
        Item { Layout.preferredHeight: 24 }
        TextField {
            id: username
            Layout.fillWidth: true
            Layout.preferredHeight: 50
            text: userModel.lastUser || ""
            placeholderText: "Username"
            color: "#ffffff"
            font.pixelSize: 16
            background: Rectangle { color: "#e0221738"; radius: 11; border.color: "#9065be" }
        }
        TextField {
            id: password
            Layout.fillWidth: true
            Layout.preferredHeight: 50
            placeholderText: "Password"
            echoMode: TextInput.Password
            color: "#ffffff"
            font.pixelSize: 16
            onAccepted: root.signIn()
            background: Rectangle { color: "#e0221738"; radius: 11; border.color: "#9065be" }
        }
        ComboBox {
            id: sessionBox
            Layout.fillWidth: true
            model: sessionModel
            textRole: "name"
            currentIndex: sessionModel.lastIndex >= 0 ? sessionModel.lastIndex : 0
        }
        Button {
            Layout.fillWidth: true
            Layout.preferredHeight: 48
            text: "SIGN IN"
            onClicked: root.signIn()
            background: Rectangle { color: "#955cdb"; radius: 12; border.color: "#d5b0ff" }
            contentItem: Text {
                text: parent.text
                color: "white"
                font.bold: true
                font.pixelSize: 15
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }
        Text {
            Layout.fillWidth: true
            color: "#ffabab"
            text: root.errorMessage
            horizontalAlignment: Text.AlignHCenter
            visible: root.errorMessage.length > 0
            wrapMode: Text.Wrap
        }
        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            spacing: 22
            Button { text: "Restart"; onClicked: sddm.reboot() }
            Button { text: "Shut down"; onClicked: sddm.powerOff() }
        }
    }
    Connections {
        target: sddm
        function onLoginFailed() {
            root.errorMessage = "Sign-in failed. Check your username and password."
            password.selectAll()
            password.forceActiveFocus()
        }
    }
    Component.onCompleted: password.forceActiveFocus()
}
