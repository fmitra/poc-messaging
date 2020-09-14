import { h } from 'preact';

const Notification = (props: { key: number; message: string }): JSX.Element => (
  <div class='notification'>
    {props.message} <br/>
  </div>
)

const Notifications = (props: { notifications: string[] }): JSX.Element => (
  <div class='notifications'>
    {props.notifications.map((m, idx): JSX.Element => (
      <Notification key={idx} message={m} />
    ))}
  </div>
);

export default Notifications;
